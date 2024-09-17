package com.cloudera.ps.csa.miniservices.statemachine.kafka;

import com.cloudera.ps.csa.miniservices.statemachine.event.Event;
import com.cloudera.ps.csa.miniservices.statemachine.generator.StandaloneThreadedGenerator;
import org.apache.flink.streaming.examples.statemachine.event.Event;
import org.apache.flink.streaming.examples.statemachine.generator.StandaloneThreadedGenerator;
import org.apache.flink.util.Collector;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.ByteArraySerializer;

import java.util.Properties;

import static org.apache.flink.util.Preconditions.checkNotNull;

/** A generator that pushes the data into Kafka. */
public class KafkaStandaloneGenerator extends StandaloneThreadedGenerator {

    public static final String BROKER_ADDRESS = "localhost:9092";

    public static final String TOPIC = "flink-demo-topic-1";

    public static final int NUM_PARTITIONS = 1;

    /** Entry point to the kafka data producer. */
    public static void main(String[] args) throws Exception {

        final KafkaCollector[] collectors = new KafkaCollector[NUM_PARTITIONS];

        // create the generator threads
        for (int i = 0; i < collectors.length; i++) {
            collectors[i] = new KafkaCollector(BROKER_ADDRESS, TOPIC, i);
        }

        StandaloneThreadedGenerator.runGenerator(collectors);
    }

    // ------------------------------------------------------------------------

    private static class KafkaCollector implements Collector<Event>, AutoCloseable {

        private final KafkaProducer<Object, byte[]> producer;

        private final EventDeSerializationSchema serializer;

        private final String topic;

        private final int partition;

        KafkaCollector(String brokerAddress, String topic, int partition) {
            this.topic = checkNotNull(topic);
            this.partition = partition;
            this.serializer = new EventDeSerializationSchema();

            // create Kafka producer
            Properties properties = new Properties();
            properties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, brokerAddress);
            properties.put(
                    ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
                    ByteArraySerializer.class.getCanonicalName());
            properties.put(
                    ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
                    ByteArraySerializer.class.getCanonicalName());
            this.producer = new KafkaProducer<>(properties);
        }

        @Override
        public void collect(Event evt) {
            byte[] serialized = serializer.serialize(evt);
            producer.send(new ProducerRecord<>(topic, partition, null, serialized));
        }

        @Override
        public void close() {
            producer.close();
        }
    }
}

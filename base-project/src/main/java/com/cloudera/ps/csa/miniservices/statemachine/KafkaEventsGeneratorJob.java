package com.cloudera.ps.csa.miniservices.statemachine;


import com.cloudera.ps.csa.miniservices.statemachine.event.Event;
import com.cloudera.ps.csa.miniservices.statemachine.generator.EventsGeneratorFunction;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.connector.source.util.ratelimit.RateLimiterStrategy;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.connector.datagen.source.DataGeneratorSource;
import org.apache.flink.connector.datagen.source.GeneratorFunction;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.examples.statemachine.event.Event;
import org.apache.flink.streaming.examples.statemachine.generator.EventsGeneratorFunction;
import org.apache.flink.streaming.examples.statemachine.kafka.EventDeSerializationSchema;

/**
 * Job to generate input events that are written to Kafka, for the {@link StateMachineExample} job.
 */
public class KafkaEventsGeneratorJob {

    public static void main(String[] args) throws Exception {

        final ParameterTool params = ParameterTool.fromArgs(args);

        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        final double errorRate = params.getDouble("error-rate", 0.0);
        final int sleep = params.getInt("sleep", 1);
        final double recordsPerSecond =
                params.getDouble("rps", rpsFromSleep(sleep, env.getParallelism()));
        System.out.printf(
                "Generating events to Kafka with standalone source with error rate %f and %.1f records per second\n",
                errorRate, recordsPerSecond);
        System.out.println();

        String kafkaTopic = params.get("kafka-topic");
        String brokers = params.get("brokers", "localhost:9092");

        GeneratorFunction<Long, Event> generatorFunction = new EventsGeneratorFunction(errorRate);
        DataGeneratorSource<Event> eventGeneratorSource =
                new DataGeneratorSource<>(
                        generatorFunction,
                        Long.MAX_VALUE,
                        RateLimiterStrategy.perSecond(recordsPerSecond),
                        TypeInformation.of(Event.class));

        env.fromSource(
                        eventGeneratorSource,
                        WatermarkStrategy.noWatermarks(),
                        "Events Generator Source")
                .sinkTo(
                        KafkaSink.<Event>builder()
                                .setBootstrapServers(brokers)
                                .setRecordSerializer(
                                        KafkaRecordSerializationSchema.builder()
                                                .setValueSerializationSchema(
                                                        new EventDeSerializationSchema())
                                                .setTopic(kafkaTopic)
                                                .build())
                                .build());

        // trigger program execution
        env.execute("State machine example Kafka events generator job");
    }

    // Used for backwards compatibility to convert legacy 'sleep' parameter to records per second.
    private static double rpsFromSleep(int sleep, int parallelism) {
        return (1000d / sleep) * parallelism;
    }
}

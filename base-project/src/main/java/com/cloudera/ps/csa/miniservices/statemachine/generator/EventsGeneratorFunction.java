package com.cloudera.ps.csa.miniservices.statemachine.generator;


import com.cloudera.ps.csa.miniservices.statemachine.event.Event;
import org.apache.flink.api.connector.source.SourceReaderContext;
import org.apache.flink.connector.datagen.source.GeneratorFunction;

import static org.apache.flink.util.Preconditions.checkArgument;

/** A generator function that produces the events on the fly. Useful for self-contained demos. */
@SuppressWarnings("serial")
public class EventsGeneratorFunction implements GeneratorFunction<Long, Event> {

    private final double errorProbability;

    transient EventsGenerator generator;
    private int min;
    private int max;

    public EventsGeneratorFunction(double errorProbability) {
        checkArgument(
                errorProbability >= 0.0 && errorProbability <= 1.0,
                "error probability must be in [0.0, 1.0]");

        this.errorProbability = errorProbability;
    }

    @Override
    public void open(SourceReaderContext readerContext) throws Exception {
        final int range = Integer.MAX_VALUE / readerContext.currentParallelism();
        min = range * readerContext.getIndexOfSubtask();
        max = min + range;
        generator = new EventsGenerator(errorProbability);
    }

    @Override
    public Event map(Long value) throws Exception {
        return generator.next(min, max);
    }
}


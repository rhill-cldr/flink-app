package com.cloudera.ps.csa.miniservices.statemachine.dfa;

import com.cloudera.ps.csa.miniservices.statemachine.event.EventType;

/** Simple combination of EventType and State. */
public class EventTypeAndState {

    public final EventType eventType;

    public final State state;

    public EventTypeAndState(EventType eventType, State state) {
        this.eventType = eventType;
        this.state = state;
    }
}

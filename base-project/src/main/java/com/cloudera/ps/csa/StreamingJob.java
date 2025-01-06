/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.cloudera.ps.csa;

import com.cloudera.ps.csa.util.*;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.RestartStrategyOptions;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.KeyedStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.co.CoFlatMapFunction;
import org.apache.flink.util.Collector;

import java.time.Duration;


public class StreamingJob {

	public static void main(String[] args) throws Exception {

		Configuration config = new Configuration();
		config.set(RestartStrategyOptions.RESTART_STRATEGY, "exponential-delay");
		config.set(RestartStrategyOptions.RESTART_STRATEGY_EXPONENTIAL_DELAY_INITIAL_BACKOFF, Duration.ofMillis(1));
		config.set(RestartStrategyOptions.RESTART_STRATEGY_EXPONENTIAL_DELAY_MAX_BACKOFF, Duration.ofMillis(1000));
		config.set(RestartStrategyOptions.RESTART_STRATEGY_EXPONENTIAL_DELAY_BACKOFF_MULTIPLIER, 1.1); // exponential multiplier
		config.set(RestartStrategyOptions.RESTART_STRATEGY_EXPONENTIAL_DELAY_RESET_BACKOFF_THRESHOLD, Duration.ofMillis(2000)); // threshold duration to reset delay to its initial value
		config.set(RestartStrategyOptions.RESTART_STRATEGY_EXPONENTIAL_DELAY_JITTER_FACTOR, 0.1); // jitter
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment(config);

		// configure watermark interval
		env.getConfig().setAutoWatermarkInterval(1000L);

		// ingest sensor stream
		DataStream<SensorReading> tempReadings = env
				// SensorSource generates random temperature readings
				.addSource(new SensorSource())
				// assign timestamps and watermarks which are required for event time
				.assignTimestampsAndWatermarks(WatermarkStrategy.forMonotonousTimestamps());
        
        tempReadings.printToErr();

		env.execute("Flink Streaming Java API");
	}

	/**
	 * A CoFlatMapFunction that processes a stream of temperature readings ans a control stream
	 * of smoke level events. The control stream updates a shared variable with the current smoke level.
	 * For every event in the sensor stream, if the temperature reading is above 100 degrees
	 * and the smoke level is high, a "Risk of fire" alert is generated.
	 */
	public static class RaiseAlertFlatMap implements CoFlatMapFunction<SensorReading, SmokeLevel, Alert> {

		private SmokeLevel smokeLevel = SmokeLevel.LOW;

		@Override
		public void flatMap1(SensorReading tempReading, Collector<Alert> out) throws Exception {
			// high chance of fire => true
			if (this.smokeLevel == SmokeLevel.HIGH && tempReading.temperature > 100) {
				out.collect(new Alert("Risk of fire! " + tempReading, tempReading.timestamp));
			}
		}

		@Override
		public void flatMap2(SmokeLevel smokeLevel, Collector<Alert> out) {
			// update smoke level
			this.smokeLevel = smokeLevel;
		}
	}
}

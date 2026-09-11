package Utils;

import java.lang.management.ManagementFactory;
import java.lang.management.ThreadMXBean;

/**
 * Provides the methods to create and use timers.
 * <p>
 * @author José Carlos Ortiz Bayliss
 * @version 1.0
 */
public final class Timer {
    
    private long timeLimit, startTime;
    private final ThreadMXBean timer;        
    
    /**
     * Creates a new instance of <code>Timer</code>.
     */
    public Timer() {
        timer = ManagementFactory.getThreadMXBean();
    }
    
    /**
     * Starts the timer.
     */
    public void start() {
        start(-1);
    }
    
    /**
     * Starts the timer with the time limit provided.
     * <p>
     * @param timeLimit The maximum time allowed for the timer to work (in milliseconds). If this
     * value is set to a negative number, no timeLimit limit is imposed to the timer.
     */
    public void start(long timeLimit) {
        if (timeLimit >= 0) {
            this.timeLimit = timeLimit * 1000000;
        } else {
            this.timeLimit = -1;
        }
        startTime = timer.getCurrentThreadCpuTime();
    }

    /**
     * Returns the elapsed time since the search started.
     * <p>
     * @return The elapsed time since the search started.
     */
    public long getElapsedTime() {
        return (timer.getCurrentThreadCpuTime() - startTime) / 1000000;
    }
    
    /**
     * Returns the remaining time for the search.
     * <p>
     * @return The remaining time for the search.
     */
    public long getRemainingTime() {        
        long tmp;
        tmp = (timeLimit - (timer.getCurrentThreadCpuTime() - startTime)) / 1000000;
        if (tmp > 0) {
            return tmp;
        }
        return 0;
    }
    
    /**
     * Verifies if the allowed running time is over.
     * <p>
     * @return <code>true</code> if the maximum allowed running time has been      * reached, <code>false</code> otherwise.
     */
    public boolean isTimeOver() {
        return (timeLimit >= 0) && (timer.getCurrentThreadCpuTime() - startTime >= timeLimit);
    }
    
}

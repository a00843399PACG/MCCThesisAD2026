package mx.tec.hermes.problems;

import mx.tec.hermes.exceptions.NoSuchFeatureException;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.text.DecimalFormat;
import mx.tec.hermes.problems.kp.KP;
import mx.tec.meta.gp.SExpression;

/**
 * Provides the basic functionality for all the problems supported by HERMES.
 *
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.1
 */
public abstract class Problem {

    /**
     * The problem Id associated to this problem.
     */
    protected String problemId = "Not available";

    /**
     * Returns the problem Id associated to this problem.
     *
     * @return The problem Id associated to this problem.
     */
    protected String getProblemId() {
        return problemId;
    }

    /**
     * Returns the size of this problem.
     *
     * @return The size of this problem. Please note that the size might mean different things according to the problem.
     */
    public abstract int getSize();
    
    /**
     * Returns the current value of a given feature.
     *
     * @param feature The name of the feature.
     * @return The current value of a given feature.
     * @throws NoSuchFeatureException
     */
    public abstract double getFeature(String feature) throws NoSuchFeatureException;

    /**
     * Returns the objective function value of the current solution to this problem.
     *
     * @return The objective function value of the current solution to this problem.
     */
    public abstract double getObjValue();

    /**
     * Solves this problem by using a specific heuristic.
     *
     * @param heuristic The heuristic to solve this problem.
     */
    public abstract void solve(String heuristic);

    /**
     * Characterizes a problem set by using a set of features.
     *
     * @param set The set of instances to characterize.
     * @param features The features to be used to characterize the set.
     * @return The characterization a problem set by using a set of features.
     */    
    public final String characterize(ProblemSet set, String[] features) {
        DecimalFormat format;
        StringBuilder string, featureValues;
        Problem problem;
        Constructor<?> constructor;
        format = new DecimalFormat("0.0000");
        string = new StringBuilder();
        string.append("INSTANCE\t");
        for (String feature : features) {
            string.append(feature).append("\t");
        }
        string.append("\r\n");
        try {
            for (String file : set.getFiles()) {
                constructor = this.getClass().getConstructor(String.class);
                problem = (Problem) constructor.newInstance(file);
                featureValues = new StringBuilder();
                string.append(problem.getProblemId()).append("\t");
                for (String feature : features) {
                    problem = (Problem) constructor.newInstance(file);                    
                    featureValues.append(format.format(problem.getFeature(feature))).append("\t");
                }
                string.append(featureValues).append("\r\n");
            }
        } catch (IllegalAccessException | IllegalArgumentException | InstantiationException | NoSuchMethodException | SecurityException | InvocationTargetException | NoSuchFeatureException e) {
            System.err.println(e);
            System.err.println("The system will halt.");
            System.exit(1);
        }
        return string.toString().trim();
    }

    /**
     * Solves a problem set by using a set of heuristics.
     *
     * @param set The set of instances to solve.
     * @param heuristics The heuristics to be used to solve the set.
     * @return The results of solving a problem set by using a set of heuristics.
     */
    public final String solve(ProblemSet set, String[] heuristics) {
        DecimalFormat format;
        StringBuilder string, objValues;
        Problem problem;
        Constructor<?> constructor;
        //format = new DecimalFormat("0.0000");
        format = new DecimalFormat("00.0000E00");
        string = new StringBuilder();
        string.append("INSTANCE\t");
        for (String heuristic : heuristics) {
            string.append(heuristic).append("\t");
        }
        string.append("\r\n");
        try {
            for (String file : set.getFiles()) {
                constructor = this.getClass().getConstructor(String.class);
                problem = (Problem) constructor.newInstance(file);
                objValues = new StringBuilder();
                string.append(problem.getProblemId()).append("\t");
                for (String heuristic : heuristics) {
                    problem = (Problem) constructor.newInstance(file);
                    problem.solve(heuristic);                    
                    objValues.append(format.format(problem.getObjValue())).append("\t");                    
                }
                string.append(objValues).append("\r\n");
            }
        } catch (IllegalAccessException | IllegalArgumentException | InstantiationException | NoSuchMethodException | SecurityException | InvocationTargetException e) {
            System.err.println(e);
            System.err.println("Problem.java/solve");
            System.err.println("The system will halt.");
            System.exit(1);
        }
        return string.toString().trim();
    }
    
    /**
     * Solves a problem set by using a set of heuristics.
     *
     * @param set The set of instances to solve.
     * @param sExpressions The S-expressions to be used to solve the set.
     * @return The results of solving a problem set by using a set of heuristics.
     */
    public final String solve(ProblemSet set, SExpression[] sExpressions) {
        DecimalFormat format;
        StringBuilder string, objValues;
        Problem problem;
        Constructor<?> constructor;
        format = new DecimalFormat("0.0000");
        string = new StringBuilder();
        string.append("INSTANCE\t");
        for (SExpression sExpression : sExpressions) {
            string.append("SE").append("\t");
        }
        string.append("\r\n");
        try {
            for (String file : set.getFiles()) {
                constructor = this.getClass().getConstructor(String.class);
                problem = (Problem) constructor.newInstance(file);
                objValues = new StringBuilder();
                string.append(problem.getProblemId()).append("\t");
                for (SExpression sExpression : sExpressions) {
                    problem = (Problem) constructor.newInstance(file);
                    ((KP)problem).solve(sExpression);
                    objValues.append(format.format(problem.getObjValue())).append("\t");
                }
                string.append(objValues).append("\r\n");
            }
        } catch (IllegalAccessException | IllegalArgumentException | InstantiationException | NoSuchMethodException | SecurityException | InvocationTargetException e) {
            System.err.println(e);
            System.err.println("The system will halt.");
            System.exit(1);
        }
        return string.toString().trim();
    }
   
    /**
     * Returns the string representation of this problem.
     *
     * @return The string representation of this problem.
     */
    @Override
    public abstract String toString();

}

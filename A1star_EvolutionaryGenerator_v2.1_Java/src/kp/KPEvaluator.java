package kp;

import meta.Evaluator;
import meta.Individual;
import util.Statistical;

public class KPEvaluator extends Evaluator {

    private final InstanceType type;
    private int[] weights;
    private double[] profits;

    public enum InstanceType {
        DEFAULT_EASY,
        DEFAULT_HARD,
        MIN_WEIGHT_EASY,
        MIN_WEIGHT_HARD,
        MAX_PROFIT_EASY,
        MAX_PROFIT_HARD,
        MAX_PROFIT_WEIGHT_EASY,
        MAX_PROFIT_WEIGHT_HARD,
        MARKOVITZ_EASY,
        MARKOVITZ_HARD,
        MIN_VARIANCE,
        MAX_VARIANCE,
        PAIRED_DEF_MAXP,
        PAIRED_DEF_MAXPW,
        PAIRED_DEF_MINW,
        PAIRED_MAXP_MAXPW,
        PAIRED_MAXP_MINW,
        PAIRED_MAXPW_MINW
    }

    public KPEvaluator(InstanceType type) {
        super();
        this.type = type;
    }

    public InstanceType getType() {
        return type;
    }

    public double[] objectiveVector(KPIndividual individual) {
        KPConfiguration configuration = individual.getConfiguration();
        if (weights == null || weights.length != configuration.nbItems) {
            weights = new int[configuration.nbItems];
            profits = new double[configuration.nbItems];
        }
        individual.decodeInto(weights, profits);
        double[] vector = new double[Heuristics.ALL.length];
        try {
            for (int h = 0; h < Heuristics.ALL.length; h++) {
                vector[h] = Heuristics.value(weights, profits, configuration.capacity, Heuristics.ALL[h]);
            }
        } catch (NoSuchHeuristicException exception) {
            System.err.println(exception);
            System.err.println("KPEvaluator.java/objectiveVector");
            System.err.println("The system will halt.");
            System.exit(1);
        }
        return vector;
    }

    @Override
    public double evaluate(Individual individual) {
        double resultDefault, resultMinWeight, resultMaxProfitPerWeightUnit, resultMaxProfit, max, lambda;
        double[] results, vector;
        nbEvaluations++;
        vector = objectiveVector((KPIndividual) individual);
        resultDefault = vector[0];
        resultMinWeight = vector[1];
        resultMaxProfitPerWeightUnit = vector[2];
        resultMaxProfit = vector[3];
        lambda = 2;
        switch (type) {
            case DEFAULT_EASY:
                results = new double[]{resultMinWeight, resultMaxProfit, resultMaxProfitPerWeightUnit};
                return resultDefault - Statistical.max(results);
            case DEFAULT_HARD:
                results = new double[]{resultMinWeight, resultMaxProfit, resultMaxProfitPerWeightUnit};
                return Statistical.min(results) - resultDefault;
            case MIN_WEIGHT_EASY:
                results = new double[]{resultDefault, resultMaxProfit, resultMaxProfitPerWeightUnit};
                return resultMinWeight - Statistical.max(results);
            case MIN_WEIGHT_HARD:
                results = new double[]{resultDefault, resultMaxProfit, resultMaxProfitPerWeightUnit};
                return Statistical.min(results) - resultMinWeight;
            case MAX_PROFIT_EASY:
                results = new double[]{resultDefault, resultMinWeight, resultMaxProfitPerWeightUnit};
                return resultMaxProfit - Statistical.max(results) ;
            case MAX_PROFIT_HARD:
                results = new double[]{resultDefault, resultMinWeight, resultMaxProfitPerWeightUnit};
                return Statistical.min(results) - resultMaxProfit;
            case MAX_PROFIT_WEIGHT_EASY:
                results = new double[]{resultDefault, resultMinWeight, resultMaxProfit};
                return resultMaxProfitPerWeightUnit - Statistical.max(results);
            case MAX_PROFIT_WEIGHT_HARD:
                results = new double[]{resultDefault, resultMinWeight, resultMaxProfit};
                return Statistical.min(results) - resultMaxProfitPerWeightUnit;
            case MAX_VARIANCE:
                results = new double[]{resultDefault, resultMinWeight, resultMaxProfit, resultMaxProfitPerWeightUnit};
                return Statistical.stdev(results);
            case MIN_VARIANCE:
                results = new double[]{resultDefault, resultMinWeight, resultMaxProfit, resultMaxProfitPerWeightUnit};
                return -1 * Statistical.stdev(results);
            case PAIRED_DEF_MAXP:
                max = Statistical.max(new double[]{resultDefault, resultMaxProfit, resultMaxProfitPerWeightUnit, resultMinWeight});
                resultDefault = resultDefault / max;
                resultMaxProfit = resultMaxProfit / max;
                resultMaxProfitPerWeightUnit = resultMaxProfitPerWeightUnit / max;
                resultMinWeight = resultMinWeight / max;
                return Math.min(resultDefault, resultMaxProfit) - Math.max(resultMaxProfitPerWeightUnit, resultMinWeight) - lambda * Math.abs(resultDefault - resultMaxProfit);
            case PAIRED_DEF_MAXPW:
                max = Statistical.max(new double[]{resultDefault, resultMaxProfit, resultMaxProfitPerWeightUnit, resultMinWeight});
                resultDefault = resultDefault / max;
                resultMaxProfit = resultMaxProfit / max;
                resultMaxProfitPerWeightUnit = resultMaxProfitPerWeightUnit / max;
                resultMinWeight = resultMinWeight / max;
                return Math.min(resultDefault, resultMaxProfitPerWeightUnit) - Math.max(resultMaxProfit, resultMinWeight) - lambda * Math.abs(resultDefault - resultMaxProfitPerWeightUnit);
            case PAIRED_DEF_MINW:
                max = Statistical.max(new double[]{resultDefault, resultMaxProfit, resultMaxProfitPerWeightUnit, resultMinWeight});
                resultDefault = resultDefault / max;
                resultMaxProfit = resultMaxProfit / max;
                resultMaxProfitPerWeightUnit = resultMaxProfitPerWeightUnit / max;
                resultMinWeight = resultMinWeight / max;
                return Math.min(resultDefault, resultMinWeight) - Math.max(resultMaxProfit, resultMaxProfitPerWeightUnit) - lambda * Math.abs(resultDefault - resultMinWeight);
            case PAIRED_MAXP_MAXPW:
                max = Statistical.max(new double[]{resultDefault, resultMaxProfit, resultMaxProfitPerWeightUnit, resultMinWeight});
                resultDefault = resultDefault / max;
                resultMaxProfit = resultMaxProfit / max;
                resultMaxProfitPerWeightUnit = resultMaxProfitPerWeightUnit / max;
                resultMinWeight = resultMinWeight / max;
                return Math.min(resultMaxProfit, resultMaxProfitPerWeightUnit) - Math.max(resultDefault, resultMinWeight) - lambda * Math.abs(resultMaxProfit - resultMaxProfitPerWeightUnit);
            case PAIRED_MAXP_MINW:
                max = Statistical.max(new double[]{resultDefault, resultMaxProfit, resultMaxProfitPerWeightUnit, resultMinWeight});
                resultDefault = resultDefault / max;
                resultMaxProfit = resultMaxProfit / max;
                resultMaxProfitPerWeightUnit = resultMaxProfitPerWeightUnit / max;
                resultMinWeight = resultMinWeight / max;
                return Math.min(resultMaxProfit, resultMinWeight) - Math.max(resultDefault, resultMaxProfitPerWeightUnit) - lambda * Math.abs(resultMaxProfit - resultMinWeight);
            case PAIRED_MAXPW_MINW:
                max = Statistical.max(new double[]{resultDefault, resultMaxProfit, resultMaxProfitPerWeightUnit, resultMinWeight});
                resultDefault = resultDefault / max;
                resultMaxProfit = resultMaxProfit / max;
                resultMaxProfitPerWeightUnit = resultMaxProfitPerWeightUnit / max;
                resultMinWeight = resultMinWeight / max;
                return Math.min(resultMaxProfitPerWeightUnit, resultMinWeight) - Math.max(resultDefault, resultMaxProfit) - lambda * Math.abs(resultMaxProfitPerWeightUnit - resultMinWeight);
            default:
                System.err.println("The option is not recognized by the system.");
                System.err.println("The system will halt.");
                System.exit(1);
        }
        return 0;
    }

}

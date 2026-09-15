import java.util.Locale;
import java.util.Random;
import java.util.TreeSet;
import kp.KPConfiguration;
import kp.KPEvaluator;
import kp.KPGenerator;
import kp.KPIndividual;
import kp.SeededIndividuals;
import meta.GeneticAlgorithm;
import meta.Individual;
import meta.TournamentSelector;

/**
 * One run of the A1* genetic algorithm with the knobs KP.evolve keeps fixed: the evaluation
 * budget, a trace of the best fitness, and an optional seeded initial population. It builds the
 * GA from the generator's own classes exactly as KP.evolve does, so with budget 100000 and
 * init=random it is the same run the campaign makes for the first instance of a seed.
 *
 *   java -cp bin:tools/experiments/bin GAExperiment TYPE n capacity maxW maxP mu pc pm k seed budget init
 *
 * init is "random" or "seeded". Output, one line each:
 *   trace,<evaluations>,<best fitness so far>        at log-spaced checkpoints and at the budget
 *   first_positive,<evaluations>                      first evaluation whose fitness was > 0, or -1
 *   final,<fitness>,<def>,<minw>,<maxpw>,<maxp>       objective vector of the best individual
 */
public final class GAExperiment {

    static final class TracingEvaluator extends KPEvaluator {

        private final TreeSet<Long> checkpoints;
        private double best = Double.NEGATIVE_INFINITY;
        private KPIndividual bestIndividual;
        long firstPositive = -1;

        TracingEvaluator(InstanceType type, long budget) {
            super(type);
            checkpoints = new TreeSet<>();
            for (long decade = 10; decade <= budget; decade *= 10) {
                for (double step : new double[]{1, 1.5, 2, 3, 5, 7}) {
                    long point = Math.round(decade * step);
                    if (point <= budget) {
                        checkpoints.add(point);
                    }
                }
            }
            checkpoints.add(100000L);
            checkpoints.add(budget);
        }

        @Override
        public double evaluate(Individual individual) {
            double fitness = super.evaluate(individual);
            if (fitness > best) {
                best = fitness;
                bestIndividual = (KPIndividual) individual.copy();
            }
            if (fitness > 0 && firstPositive < 0) {
                firstPositive = nbEvaluations;
            }
            if (checkpoints.contains(nbEvaluations)) {
                System.out.println("trace," + nbEvaluations + "," + best);
            }
            return fitness;
        }
    }

    public static void main(String[] args) {
        Locale.setDefault(Locale.US);
        KPEvaluator.InstanceType type = KPEvaluator.InstanceType.valueOf(args[0]);
        KPConfiguration configuration = new KPConfiguration(Integer.parseInt(args[1]), Integer.parseInt(args[2]),
                Integer.parseInt(args[3]), Integer.parseInt(args[4]));
        int mu = Integer.parseInt(args[5]);
        double pc = Double.parseDouble(args[6]);
        double pm = Double.parseDouble(args[7]);
        int k = Integer.parseInt(args[8]);
        long seed = Long.parseLong(args[9]);
        long budget = Long.parseLong(args[10]);
        boolean seeded = args[11].equals("seeded");

        // Run.execute draws the generator and selector seeds this way for instance 0.
        Random random = new Random(seed);
        long generatorSeed = random.nextLong();
        long selectorSeed = random.nextLong();
        KPGenerator random_generator = new KPGenerator(generatorSeed, configuration);
        meta.Generator generator = random_generator;
        if (seeded) {
            Random seeds = new Random(generatorSeed);
            generator = new meta.Generator() {
                @Override
                public Individual generate() {
                    return SeededIndividuals.build(type, configuration, seeds.nextLong());
                }
            };
        }
        TracingEvaluator evaluator = new TracingEvaluator(type, budget);
        GeneticAlgorithm ga = new GeneticAlgorithm(evaluator, generator, new TournamentSelector(k, selectorSeed),
                GeneticAlgorithm.Objective.MAXIMIZE);
        KPIndividual returned = (KPIndividual) ga.run(mu, budget, pc, pm, GeneticAlgorithm.Type.GENERATIONAL, false);
        System.out.println("first_positive," + evaluator.firstPositive);
        double[] v = evaluator.objectiveVector(evaluator.bestIndividual);
        System.out.println("final," + evaluator.evaluate(evaluator.bestIndividual) + "," + v[0] + "," + v[1] + ","
                + v[2] + "," + v[3] + ",ga_best=" + returned.getEvaluation());
    }
}

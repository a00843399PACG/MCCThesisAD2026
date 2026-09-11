/*
 * Reference harness: runs a fixed scenario against the sources of
 * EvolutionaryGenerator_v2.1_Java to produce ``expected_java_output.txt``, the
 * golden file that ``tests/test_equivalence.py`` compares the translation with.
 *
 * Compile and run it from the ``tests`` directory:
 *   javac -cp <clases del proyecto Java> -d <destino> java/Reference.java
 *   java  -cp <destino> Reference instances > expected_java_output.txt
 *
 * @author Paola Azeneth Castillo Gutierrez
 */

import java.util.*;
import mx.tec.hermes.problems.*;
import mx.tec.hermes.problems.kp.*;
import mx.tec.hermes.problems.kp.generator.*;
import mx.tec.hermes.utils.Statistical;
import mx.tec.meta.*;
import mx.tec.meta.ga.GeneticAlgorithm;
import mx.tec.meta.ga.GeneticAlgorithm.Objective;
import mx.tec.meta.mga.MicroGeneticAlgorithm;
import mx.tec.meta.es.EvolutionaryStrategy;
import mx.tec.meta.gp.*;

public class Reference {
    static String f(double d) { return Long.toHexString(Double.doubleToRawLongBits(d)); }
    static String f(double[] d) { StringBuilder s = new StringBuilder(); for (double x : d) s.append(f(x)).append(" "); return s.toString().trim(); }

    public static void main(String[] args) {
        String pool = args[0];
        double[] v = new double[]{3.5, -1.25, 7.0, 2.0, -9.5, 4.25};
        double[] w = new double[]{1.0, 2.0, 3.0, 4.0, 5.0, 6.5};
        double[] neg = new double[]{-1.0, -2.0, -3.0};
        System.out.println("=== STATISTICAL ===");
        System.out.println("mean " + f(Statistical.mean(v)));
        System.out.println("stdev " + f(Statistical.stdev(v)));
        System.out.println("median " + f(Statistical.median(v)));
        System.out.println("correlation " + f(Statistical.correlation(v, w)));
        System.out.println("lowerQuartile " + f(Statistical.lowerQuartile(v)));
        System.out.println("upperQuartile " + f(Statistical.upperQuartile(v)));
        System.out.println("sort " + f(Statistical.sort(v)));
        System.out.println("max " + f(Statistical.max(v)));
        System.out.println("min " + f(Statistical.min(v)));
        System.out.println("range " + f(Statistical.range(v)));
        System.out.println("maxOfNegatives " + f(Statistical.max(neg)));
        System.out.println("meanEmpty " + f(Statistical.mean(new double[0])));
        System.out.println("stdevSingle " + f(Statistical.stdev(new double[]{5.0})));

        System.out.println("=== KPINDIVIDUAL ===");
        KPIndividual.setCapacity(20);
        KPIndividual.setMaxWeightPerItem(20);
        KPIndividual.setMaxProfitPerItem(50);
        KPIndividual.setNbItems(10);
        KPIndividual a = new KPIndividual(7L);
        KPIndividual b = new KPIndividual(99L);
        System.out.println("a " + a);
        System.out.println("b " + b);
        System.out.println("aKP " + a.toKP());
        Individual[] kids = a.combine(b, 1.0);
        System.out.println("kid0 " + kids[0]);
        System.out.println("kid1 " + kids[1]);
        kids[0].mutate(0.3);
        System.out.println("kid0mut " + kids[0]);
        System.out.println("copy " + kids[0].copy());
        KPIndividual.setMaxWeightPerItem(100);
        KPIndividual.setMaxProfitPerItem(1000);
        KPIndividual.setNbItems(4);
        System.out.println("nbBitsWide " + new KPIndividual(3L).toKP());
        KPIndividual.setMaxWeightPerItem(20);
        KPIndividual.setMaxProfitPerItem(50);
        KPIndividual.setNbItems(10);

        System.out.println("=== SOLVE CA / X ===");
        ProblemSet set = new ProblemSet(pool);
        String file = set.getFiles().get(0);
        KP p = new KP(file);
        p.solveCA(new String[]{"MAX_PROFIT", "MIN_WEIGHT"}, new int[]{0, 1, 1});
        System.out.println("solveCA " + f(p.getObjValue()) + " " + Arrays.toString(p.getSolution()));
        System.out.println("knapsack " + p.getKnapsack());
        System.out.println("size " + p.getSize() + " items " + p.getItems());
        new KP(file).solveX(file, KP.HEURISTICS, 2020L);

        System.out.println("=== PROBLEM SET / STREAM ===");
        ProblemSet train = new ProblemSet(pool, ProblemSet.Subset.TRAIN, 0.5, 77L);
        ProblemSet test = new ProblemSet(pool, ProblemSet.Subset.TEST, 0.5, 77L);
        System.out.println("train " + train.getFiles() + " size " + train.getSize());
        System.out.println("test " + test.getFiles() + " size " + test.getSize());
        ProblemStream stream = new ProblemStream(pool, 5L);
        for (int i = 0; i < 6; i++) System.out.println("stream " + stream.next());

        System.out.println("=== GA STEADY STATE ===");
        GeneticAlgorithm ga = new GeneticAlgorithm(new KPEvaluator(KPEvaluator.InstanceType.MIN_VARIANCE),
                new KPGenerator(11L), new TournamentSelector(3, 13L), Objective.MINIMIZE);
        System.out.println("best " + ga.run(6, 200, 0.9, 0.05, GeneticAlgorithm.Type.STEADY_STATE, true));

        System.out.println("=== GA GENERATIONAL ===");
        GeneticAlgorithm gag = new GeneticAlgorithm(new KPEvaluator(KPEvaluator.InstanceType.MAX_PROFIT_WEIGHT_HARD),
                new KPGenerator(61L), new TournamentSelector(4, 63L), Objective.MAXIMIZE);
        System.out.println("best " + gag.run(6, 180, 1.0, 0.1, GeneticAlgorithm.Type.GENERATIONAL, true));

        System.out.println("=== MGA GENERATIONAL ===");
        MicroGeneticAlgorithm mga = new MicroGeneticAlgorithm(new KPEvaluator(KPEvaluator.InstanceType.MAX_VARIANCE),
                new KPGenerator(21L), new TournamentSelector(2, 23L), Objective.MAXIMIZE);
        System.out.println("best " + mga.run(4, 120, MicroGeneticAlgorithm.Type.GENERATIONAL, true));

        System.out.println("=== MGA STEADY STATE ===");
        MicroGeneticAlgorithm mga2 = new MicroGeneticAlgorithm(new KPEvaluator(KPEvaluator.InstanceType.PAIRED_DEF_MAXP),
                new KPGenerator(31L), new TournamentSelector(2, 33L), Objective.MAXIMIZE);
        System.out.println("best " + mga2.run(4, 120, MicroGeneticAlgorithm.Type.STEADY_STATE, true));

        System.out.println("=== ES ===");
        EvolutionaryStrategy es = new EvolutionaryStrategy(new KPEvaluator(KPEvaluator.InstanceType.DEFAULT_HARD));
        System.out.println("best " + es.run(new KPIndividual(41L), 50, 0.2, true));

        System.out.println("=== SEXPRESSION ===");
        SExpression.init(new String[]{"w", "p", "R"}, new String[]{"+", "-", "*", "/", "^", "exp", "log", "log10"}, 1234L);
        SExpression.set("w", 3.0);
        SExpression.set("p", 12.0);
        for (int i = 0; i < 5; i++) {
            SExpression se = new SExpression(0);
            System.out.println("se " + se + " size " + se.getSize() + " eval " + f(se.evaluate()) + " copy " + se.copy());
        }
        System.out.println("=== GP ===");
        SExpression.init(new String[]{"w", "p", "R"}, new String[]{"+", "-", "*", "/"}, 4321L);
        GPGenerator gpg = new GPGenerator(51L);
        GPIndividual g1 = (GPIndividual) gpg.generate();
        GPIndividual g2 = (GPIndividual) gpg.generate();
        System.out.println("g1 " + g1);
        System.out.println("g2 " + g2);
        Individual[] gkids = g1.combine(g2, 1.0);
        System.out.println("gkid0 " + gkids[0]);
        System.out.println("gkid1 " + gkids[1]);
        gkids[0].mutate(1.0);
        System.out.println("gkid0mut " + gkids[0]);
        KP kpse = new KP(file);
        kpse.solve(new SExpression(0));
        System.out.println("solveSE " + f(kpse.getObjValue()));
        System.out.println("=== SOLVE SE SET ===");
        System.out.println(new KP().solve(set, new SExpression[]{new SExpression(0), new SExpression(0)}));
    }
}

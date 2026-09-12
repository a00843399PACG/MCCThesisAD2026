import kp.Heuristics;
import kp.KPConfiguration;
import java.util.Random;

/**
 * Estimates the measure of the target sets under the uniform law U_theta, with no engine.
 *
 * The attainability of a labelled type falls with n in the characterisation campaign, but a
 * campaign runs a fixed budget of 10^5 evaluations and a population of 10 while the genotype
 * space grows, so a falling attainment rate has two possible readings: the target set shrinks,
 * or a fixed budget buys less. This separates them. It draws instances from U_theta directly --
 * per item, (w, p) uniform on {1..2^bw} x {1..2^bp}, which is exactly the law of
 * KPGenerator.generate() -- and counts how often each heuristic strictly wins and strictly
 * loses. No search, no elite, no budget.
 *
 * The packings come from kp.Heuristics, the same class the generator evaluates with, so the
 * two numbers are commensurable.
 *
 * usage: java -cp bin:tools TargetMeasure <n> <bits> <alpha> <draws> <seed>
 * prints one CSV row: n,bits,alpha,c,draws,win_def,win_minw,win_maxpw,win_maxp,
 *                     lose_def,lose_minw,lose_maxpw,lose_maxp
 */
public final class TargetMeasure {

    /** Same derivation the campaign uses: c from the expected total weight. */
    static int capacityFor(int n, int bits, double alpha) {
        double expected = n * ((1L << bits) + 1) / 2.0;
        return (int) Math.max(1, Math.round(alpha * expected));
    }

    public static void main(String[] args) throws Exception {
        int n = Integer.parseInt(args[0]);
        int bits = Integer.parseInt(args[1]);
        double alpha = Double.parseDouble(args[2]);
        int draws = Integer.parseInt(args[3]);
        long seed = Long.parseLong(args[4]);

        int bound = 1 << bits;
        int c = capacityFor(n, bits, alpha);
        new KPConfiguration(n, c, bound, bound);   // validates the widths

        Random random = new Random(seed);
        int[] weights = new int[n];
        double[] profits = new double[n];
        int[] wins = new int[4], losses = new int[4];

        for (int d = 0; d < draws; d++) {
            for (int i = 0; i < n; i++) {
                weights[i] = random.nextInt(bound) + 1;
                profits[i] = random.nextInt(bound) + 1;
            }
            double[] v = new double[4];
            for (int h = 0; h < 4; h++) {
                v[h] = Heuristics.value(weights, profits, c, Heuristics.ALL[h]);
            }
            for (int h = 0; h < 4; h++) {
                boolean strictWin = true, strictLoss = true;
                for (int g = 0; g < 4; g++) {
                    if (g == h) continue;
                    if (v[h] <= v[g]) strictWin = false;
                    if (v[h] >= v[g]) strictLoss = false;
                }
                if (strictWin) wins[h]++;
                if (strictLoss) losses[h]++;
            }
        }

        // Heuristics.ALL is {DEFAULT, MIN_WEIGHT, MAX_PROFIT/WEIGHT, MAX_PROFIT}
        StringBuilder row = new StringBuilder();
        row.append(n).append(',').append(bits).append(',').append(alpha).append(',')
           .append(c).append(',').append(draws);
        for (int h = 0; h < 4; h++) row.append(',').append((double) wins[h] / draws);
        for (int h = 0; h < 4; h++) row.append(',').append((double) losses[h] / draws);
        System.out.println(row);
    }
}

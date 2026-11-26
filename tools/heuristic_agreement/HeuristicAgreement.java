import java.util.Arrays;
import java.util.Comparator;
import java.nio.file.*; import java.util.*; import java.io.*;

public final class HeuristicAgreement {
    public static void main(String[] args) throws Exception {
        Path root = Paths.get(args[0]);
        try (PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter(args[1])));
             java.util.stream.Stream<Path> s = Files.walk(root)) {
            out.println("file,j_def,j_minw,j_maxpw,j_maxp");
            Iterator<Path> it = s.filter(p -> p.toString().endsWith(".kp")).sorted().iterator();
            while (it.hasNext()) {
                Path p = it.next();
                List<String> lines = Files.readAllLines(p);
                String[] h = lines.get(0).split(",");
                int n = Integer.parseInt(h[0].trim()), c = Integer.parseInt(h[1].trim());
                int[] w = new int[n]; double[] pr = new double[n];
                for (int i = 0; i < n; i++) {
                    String[] f = lines.get(i + 1).split(",");
                    w[i] = Integer.parseInt(f[0].trim()); pr[i] = Double.parseDouble(f[1].trim());
                }
                StringBuilder b = new StringBuilder(root.relativize(p).toString());
                for (String hh : Heuristics.ALL) b.append(',').append(Heuristics.value(w, pr, c, hh));
                out.println(b);
            }
        }
    }
}
class NoSuchHeuristicException extends RuntimeException { NoSuchHeuristicException(String m){super(m);} }


final class Heuristics {

    public static final String DEFAULT = "DEFAULT";
    public static final String MAX_PROFIT = "MAX_PROFIT";
    public static final String MAX_PROFIT_WEIGHT = "MAX_PROFIT/WEIGHT";
    public static final String MIN_WEIGHT = "MIN_WEIGHT";
    public static final String[] ALL = {DEFAULT, MIN_WEIGHT, MAX_PROFIT_WEIGHT, MAX_PROFIT};

    private Heuristics() {
    }

    public static Integer[] order(int[] weights, double[] profits, String heuristic) throws NoSuchHeuristicException {
        int n = weights.length;
        Integer[] index = new Integer[n];
        for (int i = 0; i < n; i++) {
            index[i] = i;
        }
        Comparator<Integer> key;
        switch (heuristic) {
            case DEFAULT:
                return index;
            case MAX_PROFIT:
                key = (a, b) -> Double.compare(profits[b], profits[a]);
                break;
            case MAX_PROFIT_WEIGHT:
                key = (a, b) -> Double.compare(profits[b] / weights[b], profits[a] / weights[a]);
                break;
            case MIN_WEIGHT:
                key = (a, b) -> Integer.compare(weights[a], weights[b]);
                break;
            default:
                throw new NoSuchHeuristicException("Heuristic '" + heuristic + "' is not recognized by the system.");
        }
        Arrays.sort(index, key);
        return index;
    }

    public static double value(int[] weights, double[] profits, int capacity, String heuristic) throws NoSuchHeuristicException {
        Integer[] order = order(weights, profits, heuristic);
        int residual = capacity;
        double total = 0.0;
        for (int i : order) {
            if (weights[i] <= residual) {
                residual -= weights[i];
                total += profits[i];
            }
        }
        return total;
    }
}

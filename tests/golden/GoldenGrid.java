import java.io.File;
import java.lang.reflect.Method;

public final class GoldenGrid {

    // The four configurations of the grid (Section 14 of the formalization).
    private static final int[][] THETA = {
        {10, 20, 20, 50},
        {12, 20, 32, 32},
        {50, 100, 17, 33},
        {100, 400, 1000, 1100}
    };

    private static final String[] TYPES = {
        "DEFAULT_EASY", "DEFAULT_HARD", "MIN_WEIGHT_EASY", "MIN_WEIGHT_HARD",
        "MAX_PROFIT_EASY", "MAX_PROFIT_HARD", "MAX_PROFIT_WEIGHT_EASY", "MAX_PROFIT_WEIGHT_HARD",
        "MIN_VARIANCE", "MAX_VARIANCE", "PAIRED_DEF_MAXP", "PAIRED_DEF_MAXPW",
        "PAIRED_DEF_MINW", "PAIRED_MAXP_MAXPW", "PAIRED_MAXP_MINW", "PAIRED_MAXPW_MINW"
    };

    private static final String[][] LAYOUTS = {
        {"mx.tec.hermes.problems.kp.KP", "mx.tec.hermes.problems.kp.generator.KPEvaluator$InstanceType"},
        {"kp.KP", "kp.KPEvaluator$InstanceType"}
    };

    /**
     * usage: java GoldenGrid &lt;outDir&gt; &lt;thetaIndex&gt; &lt;seeds&gt; &lt;nbInstances&gt; [typeIndex]
     *
     * One theta per invocation, and optionally one type, so that golden.py can shard the grid
     * across processes. The seed law and the engine parameters do not depend on the sharding,
     * so any sharding emits the same files.
     */
    public static void main(String[] args) throws Exception {
        String outDir = args[0];
        int thetaIndex = Integer.parseInt(args[1]);
        int seeds = Integer.parseInt(args[2]);
        int nbInstances = Integer.parseInt(args[3]);
        int onlyType = args.length > 4 ? Integer.parseInt(args[4]) : -1;

        Class<?> kp = null, instanceType = null;
        for (String[] layout : LAYOUTS) {
            try {
                kp = Class.forName(layout[0]);
                instanceType = Class.forName(layout[1]);
                break;
            } catch (ClassNotFoundException ignored) {
            }
        }
        if (kp == null) {
            System.err.println("GoldenGrid: no known layout on the classpath");
            System.exit(1);
        }
        Method valueOf = instanceType.getMethod("valueOf", String.class);
        Method generate = kp.getMethod("generate", instanceType, int.class, String.class, String.class,
                int.class, int.class, int.class, int.class, int.class, double.class, double.class,
                int.class, long.class);

        // The generator prints a fitness trace per generation; the grid does not want it.
        java.io.PrintStream stdout = System.out;
        java.io.PrintStream quiet = new java.io.PrintStream(java.io.OutputStream.nullOutputStream());

        int[] t = THETA[thetaIndex];
        int n = t[0], c = t[1], w = t[2], p = t[3];
        String path = outDir + "/theta" + thetaIndex + "/";
        new File(path).mkdirs();
        for (int ti = 0; ti < TYPES.length; ti++) {
            if (onlyType >= 0 && ti != onlyType) {
                continue;
            }
            String typeName = TYPES[ti];
            Object type = valueOf.invoke(null, typeName);
            for (int s = 1; s <= seeds; s++) {
                long seed = 100003L * (thetaIndex + 1) + 1009L * s;
                String id = typeName + "_s" + s;
                System.setOut(quiet);
                generate.invoke(null, type, nbInstances, id, path, n, c, w, p, 10, 0.8, 0.1, 3, seed);
                System.setOut(stdout);
            }
        }
    }

    public static int nbThetas() {
        return THETA.length;
    }

    public static int nbTypes() {
        return TYPES.length;
    }
}

import kp.KP;
import kp.KPEvaluator;

public final class Ch5Rerun {
    public static void main(String[] a) throws Exception {
        String out = a[0];
        String type = a[1];
        int n = Integer.parseInt(a[2]), c = Integer.parseInt(a[3]), w = Integer.parseInt(a[4]), p = Integer.parseInt(a[5]);
        double pm = Double.parseDouble(a[6]);
        long seed = Long.parseLong(a[7]);
        int nb = Integer.parseInt(a[8]);
        String id = a[9];
        java.io.PrintStream stdout = System.out;
        System.setOut(new java.io.PrintStream(java.io.OutputStream.nullOutputStream()));
        new java.io.File(out).mkdirs();
        KP.generate(KPEvaluator.InstanceType.valueOf(type), nb, id, out + "/", n, c, w, p, 10, 0.8, pm, 3, seed);
        System.setOut(stdout);
    }
}

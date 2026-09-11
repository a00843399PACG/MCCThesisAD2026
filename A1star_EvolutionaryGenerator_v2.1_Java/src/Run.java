import java.io.File;
import java.util.Locale;
import java.util.Random;
import kp.KP;
import kp.KPConfiguration;
import kp.KPEvaluator;
import kp.KPIndividual;

public final class Run {

    private final KPEvaluator.InstanceType type;
    private final int nbInstances;
    private final String id;
    private final String path;
    private final KPConfiguration configuration;
    private final int populationSize;
    private final double crossoverRate;
    private final double mutationRate;
    private final int tournamentSize;
    private final long seed;
    private final boolean requireStrict;
    private final int maxRetries;

    private Run(String[] args) {
        type = KPEvaluator.InstanceType.valueOf(args[0]);
        nbInstances = Integer.parseInt(args[1]);
        id = args[2];
        path = args[3].endsWith("/") ? args[3] : args[3] + "/";
        configuration = new KPConfiguration(Integer.parseInt(args[4]), Integer.parseInt(args[5]),
                Integer.parseInt(args[6]), Integer.parseInt(args[7]));
        populationSize = Integer.parseInt(args[8]);
        crossoverRate = Double.parseDouble(args[9]);
        mutationRate = Double.parseDouble(args[10]);
        tournamentSize = Integer.parseInt(args[11]);
        seed = Long.parseLong(args[12]);
        requireStrict = flag(args, "-require-strict");
        maxRetries = option(args, "-max-retries", 10);
    }

    public static void main(String[] args) {
        Locale.setDefault(Locale.US);
        if (args.length < 13) {
            System.err.println(USAGE);
            System.exit(1);
        }
        new Run(args).execute();
    }

    private static boolean isLabelled(KPEvaluator.InstanceType type) {
        String name = type.name();
        return name.endsWith("_EASY") || name.endsWith("_HARD");
    }

    private boolean accepted(KPIndividual elite) {
        return !(requireStrict && isLabelled(type)) || elite.getEvaluation() > 0;
    }

    private void execute() {
        new File(path).mkdirs();
        if (!requireStrict) {
            KP.generate(type, nbInstances, id, path, configuration.nbItems, configuration.capacity,
                    configuration.maxWeightPerItem, configuration.maxProfitPerItem,
                    populationSize, crossoverRate, mutationRate, tournamentSize, seed);
            return;
        }
        Random random = new Random(seed);
        for (int i = 0; i < nbInstances; i++) {
            KPIndividual elite = null;
            int attempts = 0;
            while (attempts <= maxRetries) {
                elite = KP.evolve(type, configuration, populationSize, crossoverRate, mutationRate, tournamentSize, random.nextLong(), random.nextLong());
                attempts++;
                if (accepted(elite)) {
                    break;
                }
                elite = null;
            }
            String fileName = KP.fileName(path, id, configuration, i);
            if (elite == null) {
                System.err.println("unattained: " + fileName + " after " + attempts + " attempts (no strict margin)");
                continue;
            }
            elite.toKP().save(fileName);
            if (attempts > 1) {
                System.err.println("accepted: " + fileName + " on attempt " + attempts);
            }
        }
    }

    private static boolean flag(String[] args, String name) {
        for (String arg : args) {
            if (arg.equals(name)) {
                return true;
            }
        }
        return false;
    }

    private static int option(String[] args, String name, int fallback) {
        for (int i = 0; i < args.length - 1; i++) {
            if (args[i].equals(name)) {
                return Integer.parseInt(args[i + 1]);
            }
        }
        return fallback;
    }

    private static final String USAGE =
            "usage: java -cp bin Run <TYPE> <nbInstances> <id> <path> <n> <c> <Wmax> <Pmax>"
            + " <populationSize> <crossoverRate> <mutationRate> <tournamentSize> <seed>"
            + " [-require-strict] [-max-retries <r>]\n"
            + "\n"
            + "  TYPE             one of the 16 dispatched members of KPEvaluator.InstanceType,\n"
            + "                   e.g. DEFAULT_EASY, MAX_PROFIT_WEIGHT_HARD, MAX_VARIANCE.\n"
            + "  -require-strict  discard a run whose elite has fitness <= 0 on an EASY/HARD type\n"
            + "                   and retry with the next pair of seeds; reports 'unattained' after\n"
            + "                   -max-retries rejections. Without the flag the behaviour is exactly\n"
            + "                   that of KP.generate.\n"
            + "\n"
            + "example: java -cp bin Run DEFAULT_EASY 2 demo out/ 10 20 20 50 10 0.8 0.1 3 12345";
}

package mx.tec.hermes.problems;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Random;

/**
 * Provides the methods to create and handle problem sets supported by HERMES.
 * 
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public class ProblemSet {
    
    private List<String> fileNames;
    
    /**
     * Defines the fraction of the set that will be used according to the purpose of the instances.
     */
    public enum Subset {

        /**
         * A subset of problems is used for training purposes.         
         */
        TRAIN,
        /**
         * A subset of instances is used for testing purposes.
         */
        TEST
    }
    
    /**
     * Creates a new instance of <code>ProblemSet</code>.
     * 
     * @param path The path where the instances are contained.     
     */
    public ProblemSet(String path) {
        this(path, Subset.TEST, 1.0, 0);
    }
       
    /**
     * Creates a new instance of <code>ProblemSet</code>.
     * 
     * @param path The path where the instances are contained.     
     * @param type The type of set to be created (training or test).
     * @param proportion The proportion of the instances used for training.
     * @param seed The seed to initialize the random number generator.
     */
    public ProblemSet(String path, Subset type, double proportion, long seed) {
        int n;
        List<String> tmp;        
        File file = new File(path);        
        if (!file.exists() || !file.isDirectory()) {
            System.err.println("The path \'" + path + "\' is not a valid directory.");
            System.err.println("The system will halt.");
            System.exit(1);
        }
        tmp = Arrays.asList(file.list());
        fileNames = new ArrayList(tmp.size());
        Collections.sort(tmp);
        for (String fileName : tmp) {
            fileNames.add(path + "/" + fileName);
        }
        if (proportion != 1.0) {
            n = (int) Math.ceil(proportion * fileNames.size());
            Collections.shuffle(fileNames, new Random(seed));
            if (type == Subset.TRAIN) {
                fileNames = fileNames.subList(0, n);
            } else {
                fileNames = fileNames.subList(n, fileNames.size());
            }
        }        
    }
        
    /**
     * Returns the size of this problem set.
     * 
     * @return The size of this problem set.
     */
    public int getSize() {
        return fileNames.size();
    }

    /**
     * Returns the names of the files in this problem set.
     *
     * @return The names of the files in this problem set.
     */
    public List<String> getFiles() {
        return fileNames;
    }
    
}

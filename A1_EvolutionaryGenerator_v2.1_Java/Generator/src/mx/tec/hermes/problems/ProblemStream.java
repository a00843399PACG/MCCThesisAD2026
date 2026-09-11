package mx.tec.hermes.problems;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import mx.tec.hermes.problems.kp.KP;

/**
 * Provides the methods to create and handle problem streams supported by HERMES.
 * 
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public class ProblemStream {
    
    private Random random;
    private List<String> fileNames;      
    
    /**
     * Creates a new instance of <code>ProblemStream</code>.
     * 
     * @param path The path where the instances are contained.     
     * @param seed The seed to initialize the random number generator.
     */
    public ProblemStream(String path, long seed) {        
        List<String> tmp;
        File file = new File(path);
        if (!file.exists() || !file.isDirectory()) {
            System.err.println("The path \'" + path + "\'is not a valid directory.");
            System.err.println("The system will halt.");
            System.exit(1);
        }
        random = new Random(seed);
        tmp = Arrays.asList(file.list());
        fileNames = new ArrayList(tmp.size());
        Collections.sort(tmp);
        for (String fileName : tmp) {
            fileNames.add(path + "/" + fileName);
        }                
    }
    
    /**
     * Returns the next filename in this stream.
     * 
     * @return The next filename in this stream.
     */
    public String next() {
        int index;
        index = random.nextInt(fileNames.size());
        return fileNames.get(index);
    }
    
}

package mx.tec.meta.gp;

import java.text.DecimalFormat;
import java.util.HashMap;
import java.util.Random;

/**
 * @author José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 1.0
 */
public class SExpression {

    private static String[] terminals;
    private static String[] operators;
    private static final DecimalFormat format = new DecimalFormat("0.0000");
    private static final int MAX_DEPTH = 3;
    private static Random random = new Random();
    private static HashMap<String, Double> variables;
    
    private final String label;    
    private final SExpression[] children;    

    public static void init(String[] terminals, String[] operators, long seed) {
        SExpression.terminals = terminals;
        SExpression.operators = operators;
        variables = new HashMap<>();
        random = new Random(seed);
    }
    
    public static void set(String variable, double value) {
        variables.put(variable, value);
    }
    
    public SExpression(int depth) {
        int id, nbChildren;
        nbChildren = 2;
        if (random.nextDouble() < (1 - Math.pow(2, depth) / Math.pow(2, MAX_DEPTH)) && depth < MAX_DEPTH) {
            id = random.nextInt(operators.length);
            label = operators[id];
            if (label.equals("exp") || label.equals("log") || label.equals("log10")) {
                nbChildren = 1;
            }
            children = new SExpression[nbChildren];
            for (int i = 0; i < nbChildren; i++) {
                children[i] = new SExpression(depth + 1);
            }
        } else {
            id = random.nextInt(terminals.length);
            if (terminals[id].equals("R")) {
                label = format.format(random.nextDouble(-1, 1));
            } else {
                label = terminals[id];
            }
            children = new SExpression[0];
        }
    }
    
    public SExpression(String label, int nbChildren) {
        this.label = label;        
        children = new SExpression[nbChildren];
        for (int i = 0; i < nbChildren; i++) {
            children[i] = null;
        }
    }

    public final SExpression set(int index, String label) {
        SExpression sExpression;
        sExpression = new SExpression(label, 0);
        children[index] = sExpression;
        return sExpression;
    }

    public final SExpression set(int index, String label, int nbChildren) {
        SExpression node;
        node = new SExpression(label, nbChildren);
        children[index] = node;
        return node;
    }

    public SExpression[] getChildren() {
        return children;
    }
    
    public int getSize() {
        int size;
        size = 1;
        for (SExpression child : this.children) {
            size += child.getSize();
        }
        return size;
    }

    public SExpression[] pick(int id, int[] counter, SExpression parent, int index) {
        SExpression[] sExpressions;        
        if (id == counter[0]) {
            if (id > 0) {
                parent.getChildren()[index] = null;
            }
            return new SExpression[]{parent, this};
        } else {            
            for (int i = 0; i < children.length; i++) {
                counter[0]++;
                sExpressions = children[i].pick(id, counter, this, i);
                if (sExpressions != null) {
                    return sExpressions;
                }
            }
        }
        return null;
    }

    public double evaluate() {
        double tmp;
        if (children.length > 0) {
            switch (label) {
                case "+":
                    return children[0].evaluate() + children[1].evaluate();
                case "-":
                    return children[0].evaluate() - children[1].evaluate();
                case "*":
                    return children[0].evaluate() * children[1].evaluate();
                case "/":
                    tmp = children[1].evaluate();
                    if (tmp != 0) {
                        return children[0].evaluate() / tmp;
                    } else {
                        return 0;
                    }
                case "^":
                    return Math.pow(children[0].evaluate(), children[1].evaluate());
                case "exp":
                    return Math.exp(children[0].evaluate());
                case "log":
                    tmp = children[0].evaluate();
                    if (tmp != 0) {
                        return 1;
                    }
                    return Math.log(Math.abs(children[0].evaluate()));
                case "log10":
                    tmp = children[0].evaluate();
                    if (tmp != 0) {
                        return 1;
                    }
                    return Math.log10(Math.abs(children[0].evaluate()));                
                default:
                    System.err.println("Operation not supported for this S-Expression.");
                    System.err.println("The system will halt.");
                    System.exit(1);
            }
        } else {
            if (variables.containsKey(label)) {
                return variables.get(label);
            } else {
                return Double.parseDouble(label);
            }
        }
        System.exit(1);
        return Double.NaN;
    }

    public SExpression copy() {
        SExpression sExpression;
        sExpression = new SExpression(label, this.children.length);
        for (int i = 0; i < this.children.length; i++) {
            sExpression.children[i] = children[i].copy();            
        }
        return sExpression;
    }

    @Override
    public String toString() {
        StringBuilder string;
        string = new StringBuilder();
        if (children.length > 0) {
            string.append("(");
            string.append(label);
            for (SExpression child : children) {
                if (child == null) {
                    string.append(" NULL");
                } else {
                    string.append(" ").append(child.toString());
                }
            }
            string.append(")");
        } else {
            string.append(label);     
        }
        return string.toString();
    }
    
    
}

package mx.tec.meta.gp;

import java.text.DecimalFormat;
import mx.tec.meta.Individual;


/**
 *
 * @author jcobayliss
 */
public class GPIndividual extends Individual {

    private final int maxDepth;    
    public SExpression sExpression;     
    
    public GPIndividual(int maxDepth, long seed) {        
        super(0, seed);            
        this.maxDepth = maxDepth; 
        sExpression = new SExpression(0);
        
    }
    
    public GPIndividual(GPIndividual individual) {
        super(individual.getEvaluation(), individual.random.nextLong());
        this.maxDepth = individual.maxDepth;        
        this.sExpression = individual.sExpression.copy();      
    }        
    
    public final SExpression getSExpression() {
        return sExpression;
    }
    
    public void setSExpression(SExpression sExpression) {
        this.sExpression = sExpression.copy();
    }
    
    public SExpression[] remove() {
        int id;
        id = random.nextInt(0, sExpression.getSize());
        return sExpression.pick(id, new int[]{0}, null, 0);
    }
    
    @Override
    public Individual[] combine(Individual individual, double crossoverRate) {        
        GPIndividual parentA, parentB;
        SExpression[] sExpressionsA, sExpressionsB, children;
        parentA = (GPIndividual) this;
        parentB = (GPIndividual) individual;
        if (random.nextDouble() < crossoverRate) {            
            //System.out.println(">> " + parentA);                
            //System.out.println(">> " + parentB);            
            sExpressionsA = parentA.remove();
            sExpressionsB = parentB.remove();              
            //System.out.println("<< " + sExpressionsA[1]);                
            //System.out.println("<< " + sExpressionsB[1]);
            if (sExpressionsA[0] == null) {
                parentA.setSExpression(sExpressionsB[1]);
            } else {
                children = sExpressionsA[0].getChildren();
                for (int i = 0; i < children.length; i++) {
                    if (children[i] == null) {
                        children[i] = sExpressionsB[1];
                    }
                }
            }
            if (sExpressionsB[0] == null) {
                parentB.setSExpression(sExpressionsA[1]);
            } else {
                children = sExpressionsB[0].getChildren();
                for (int i = 0; i < children.length; i++) {
                    if (children[i] == null) {
                        children[i] = sExpressionsA[1];
                    }
                }
            }
        }
        return new Individual[]{parentA, parentB};
   }

    @Override
    public void mutate(double mutationRate) {
        SExpression[] sExpressions, children;
        GPGenerator generator;
        if (random.nextDouble() < mutationRate) {
            generator = new GPGenerator(random.nextLong());
            sExpressions = this.remove();
            if (sExpressions[0] == null) {
                this.setSExpression(sExpressions[1]);
            } else {
                children = sExpressions[0].getChildren();
                for (int i = 0; i < children.length; i++) {
                    if (children[i] == null) {
                        children[i] = ((GPIndividual) generator.generate()).getSExpression();
                    }
                }
            }
        }
    }

    @Override
    public Individual copy() {
        return new GPIndividual(this);
    }

    @Override
    public String toString() {
        return sExpression.toString();
    }
    
}

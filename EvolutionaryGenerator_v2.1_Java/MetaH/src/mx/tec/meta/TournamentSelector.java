package mx.tec.meta;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import mx.tec.meta.ga.GeneticAlgorithm;

/**
 * Provides the methods to use a tournament selector to be used by a genetic algorithm.
 *
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public class TournamentSelector extends Selector {

    private final int tournamentSize;

    /**
     * Creates a new instance of <code>TournamentSelector</code>.
     *
     * @param tournamentSize The size of the tournament.
     * @param seed The seed to initialize the random number generator to be used by this selector.
     */
    public TournamentSelector(int tournamentSize, long seed) {
        super(seed);
        this.tournamentSize = tournamentSize;
    }

    @Override
    public Individual[] select(List<Individual> population, GeneticAlgorithm.Objective objective) {
        List<Individual> tmp;
        Individual[] individuals;
        individuals = new Individual[2];
        for (int i = 0; i < individuals.length; i++) {
            tmp = new ArrayList(tournamentSize);
            for (int j = 0; j < tournamentSize; j++) {
                tmp.add(population.get(random.nextInt(population.size())));
            }
            if (objective == GeneticAlgorithm.Objective.MINIMIZE) {
                Collections.sort(tmp);
            } else {
                Collections.sort(tmp, Collections.reverseOrder());
            }            
            individuals[i] = (Individual) tmp.get(0).copy();
        }
        return individuals;
    }

}

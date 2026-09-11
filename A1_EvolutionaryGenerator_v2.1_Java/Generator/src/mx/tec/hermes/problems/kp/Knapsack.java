package mx.tec.hermes.problems.kp;

import java.util.LinkedList;
import java.util.List;

/**
 * Provides the methods to create and use knapsacks for the knapsack problem.
 * 
 * @author José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public class Knapsack {

    private int capacity;
    private double sProfit, pProfit;
    private final List<Item> items;

    /**
     * Creates a new instance of <code>Knapsack</code>.
     *
     * @param capacity The capacity of this knapsack.
     */
    public Knapsack(int capacity) {
        this.capacity = capacity;
        sProfit = 0;
        pProfit = 1;
        items = new LinkedList();
    }    
    
    /**
     * Returns the current capacity of this knapsack.
     *
     * @return The current capacity of this knapsack.
     */
    public int getCapacity() {
        return capacity;
    }   
    
    /**
     * Returns the current sum of profits in this knapsack.
     *
     * @return The current sum of profits in this knapsack.
     */
    public double getSumOfProfit() {
        return sProfit;
    }
    
    /**
     * Returns the current product of profits in this knapsack.
     *
     * @return The current product of profits in this knapsack.
     */
    public double getProductOfProfit() {
        return pProfit;
    }
   
    int[] getSolution(int nbItems) {
        int[] solution = new int[nbItems];
        for (Item item : items) {
            solution[item.getId()] = 1;
        }
        return solution;
    }
    
    /**
     * Revises if the item provided can be packed in this knapsack.
     *
     * @param item The item to be packed.
     * @return <code>true</code> if the item can be packed in this knapsack, <code>false</code> otherwise.
     */
    public boolean canPack(Item item) {
        return item.getWeight() <= getCapacity();
    }

    /**
     * Packs an item into this knapsack.
     *
     * @param item The item to pack.
     * @return <code>true</code> if the item was successfully packed, <code>false</code> otherwise.
     */
    public boolean pack(Item item) {
        if (item.getWeight() <= capacity) {
            items.add(item);
            capacity -= item.getWeight();
            sProfit += item.getProfit();
            pProfit *= item.getProfit();
            return true;
        }
        return false;
    }

    /**
     * Clones this knapsack.
     * 
     * @return A deep copy of this knapsack-
     */
    public Knapsack copy() {
        Knapsack tmp;
        tmp = new Knapsack(capacity);
        for (Item item : items) {
            tmp.pack(item);
        }
        return tmp;
    }
    
    /**
     * Returns the string representation of this knapsack.
     *
     * @return The string representation of this knapsack.
     */
    @Override
    public String toString() {
        StringBuilder string;
        string = new StringBuilder();
        for (Item item : items) {
            string.append(item.toString()).append(" ");
        }
        return string.toString().trim();
    }

}

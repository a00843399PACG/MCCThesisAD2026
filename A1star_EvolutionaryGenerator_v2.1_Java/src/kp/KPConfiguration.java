package kp;

public final class KPConfiguration {

    public final int nbItems;
    public final int capacity;
    public final int maxWeightPerItem;
    public final int maxProfitPerItem;
    public final int bitsWeight;
    public final int bitsProfit;
    public final int bitsBlock;
    public final int nbBits;

    public KPConfiguration(int nbItems, int capacity, int maxWeightPerItem, int maxProfitPerItem) {
        this.nbItems = nbItems;
        this.capacity = capacity;
        this.maxWeightPerItem = maxWeightPerItem;
        this.maxProfitPerItem = maxProfitPerItem;
        this.bitsWeight = ceilLog2(maxWeightPerItem);
        this.bitsProfit = ceilLog2(maxProfitPerItem);
        this.bitsBlock = bitsWeight + bitsProfit;
        this.nbBits = nbItems * bitsBlock;
    }

    public static int ceilLog2(int value) {
        if (value <= 1) {
            return 0;
        }
        return 32 - Integer.numberOfLeadingZeros(value - 1);
    }

    @Override
    public String toString() {
        return "KPConfiguration(n=" + nbItems + ", c=" + capacity + ", Wmax=" + maxWeightPerItem
                + ", Pmax=" + maxProfitPerItem + ", bw=" + bitsWeight + ", bp=" + bitsProfit + ", L=" + nbBits + ")";
    }
}

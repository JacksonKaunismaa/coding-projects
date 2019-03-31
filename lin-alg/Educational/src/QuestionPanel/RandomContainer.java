//----------------------------------------------------------------------------------------|
//  RandomContainer.java - holder to turn random numbers in questions into actual values at|
//  runtime, including ids for them to be referred to later, what the answers are stored as|
//----------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                             |
//  Date: 2019-01-15                                                                      |
//----------------------------------------------------------------------------------------|
//  Input:A range from lo to hi                                                 |
//  Output: that outputs a random value in that range                                                 |
//----------------------------------------------------------------------------------------|
package QuestionPanel;

import java.util.concurrent.ThreadLocalRandom;

public class RandomContainer {
    private double value;
    private int ID;

    RandomContainer(double value) {
        this.value = value;
    }

    RandomContainer(String lo, String hi, int ID) {
        this(Double.parseDouble(lo), Double.parseDouble(hi), ID);
    }

    RandomContainer(double lo, double hi, int ID) {
        this.value = ThreadLocalRandom.current().nextDouble(lo, hi);
        this.ID = ID;
    }

    public double getValue() {
        return value;
    }

    public int getID() {
        return ID;
    }

    public boolean close(double guess, double relTolerance, double absTolerance) {
        return Math.abs((guess - value) / (guess + value)) < relTolerance || Math.abs(guess - value) < absTolerance;
    }

    public boolean close(double guess) {
        double defaultRelativeTolerance = 0.02;
        double defaultAbsoluteTolerance = 0.15;
        return close(guess, defaultRelativeTolerance, defaultAbsoluteTolerance);
    }

    @Override
    public String toString() {
        return String.format("%.1f", value);
    }
}

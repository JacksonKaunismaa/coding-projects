package MathBase;

public class BasisVector {
    private double x, y;

    BasisVector() {
        this.x = 0;
        this.y = 0;
    }


    BasisVector(double x, double y) {
        this.x = x;
        this.y = y;
    }

    public double getVectorX() {
        return x;
    }

    public double getVectorY() {
        return y;
    }

    public String toString() {
        return "BasisVector([x = " + x + ", y = " + y + "])";
    }

}

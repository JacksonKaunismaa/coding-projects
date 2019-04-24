//----------------------------------------------------------------------------------------|
//  Vector2D.java - Most basic class, foundation for all grid drawing, vector drawing,    |
//  arrow drawing, line drawing, linear transformation animating, but simply it just holds|
//  2 values, x and y, that hold the position of the vector, plys you can do tons of      |
//  vector operations like scaling, addition, normalization, and more                     |
//----------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                             |
//  Date: 2019-01-15                                                                      |
//----------------------------------------------------------------------------------------|
//  Input: See constructor methods                                                        |
//  Output: Visual representation of vector on a grid, or arrows                          |
//----------------------------------------------------------------------------------------|
package MathBase;

import java.awt.*;

import static MathBase.LinalgGrid.ORIGIN_X;
import static MathBase.LinalgGrid.ORIGIN_Y;

public class Vector2D {
    private static final double width = 50, defaultArrowHeadSize = 0.3, gridSize = 80.0;  // width is for drawing grid
    private double x, y;
    private Polygon triangleTip = null;
    private Color color;
    private Integer ID;
    private Vector2D offset;

    private Vector2D() {
        this(0, 0);
    }

    public Vector2D(Vector2D copyVector) {    // ID==null is either meaningless (is never added to grid) or is determined when you actually add it to the grid, to ensure unique IDs
        this(copyVector.getVectorX(), copyVector.getVectorY(), copyVector.color, (Integer) null);
    }


    public Vector2D(double x, double y) {
        this(x, y, Color.gray, (Integer) null);
    }

    public Vector2D(double x, double y, Color color) {
        this(x, y, color, (Integer) null);
    }

    public Vector2D(double x, double y, Color color, String ID) {   // called in file reading
        this(x, y, color, (ID == null || ID.equals("")) ? null : Integer.parseInt(ID));
    }

    public Vector2D(double x, double y, String ID) {
        this(x, y, Color.gray, ID);
    }

    private Vector2D(double x, double y, Color color, Integer ID) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.ID = ID;
        this.offset = null;
    }

    public Vector2D(Point mousePos, Vector2D iHat, Vector2D jHat) {
        this();
        setScreenPos(mousePos.x, mousePos.y, iHat, jHat);
    }

    private double dot(Vector2D dotThis) {
        // Returns the dot product between the vector and the input
        return this.x * dotThis.x + this.y * dotThis.y;
    }

    private double dist(double pointX, double pointY) {
        pointX = (pointX - ORIGIN_X) / gridSize;
        pointY = (pointY - ORIGIN_Y) / gridSize;
        return Math.sqrt((x - pointX) * (x - pointX) + (y + pointY) * (y + pointY));
    }

    boolean clicked(double mouseX, double mouseY) {
        if (triangleTip != null && triangleTip.contains(mouseX, mouseY)) return true;
        else return dist(mouseX, mouseY) <= 0.2;
    }

    private double getMagnitude() {
        return Math.sqrt(this.dot(this));
    }

    private double getScreenMagnitude(Vector2D iHat, Vector2D jHat) {
        double dX = getScreenX(iHat, jHat) - ORIGIN_X;
        double dY = getScreenY(iHat, jHat) - ORIGIN_Y;
        return Math.sqrt(dX * dX + dY * dY) / gridSize;
    }


    Vector2D norm() {
        // Returns a copy of the vector normalized so it has euclidean norm of 1, but in the same direction
        double mag = getMagnitude();
        if (mag != 0)
            return this.scale(1. / mag);
        return new Vector2D();
    }

    private Vector2D orthonorm() {
        // Returns a copy of the vector normalized so it has euclidean norm of 1, but perpendicular to the other
        return (new Vector2D(-y, x)).norm();
    }

    Vector2D scale(double amount) {
        Vector2D newVec = new Vector2D(this);
        newVec.x *= amount;
        newVec.y *= amount;
        return newVec;
    }

    void assign(Vector2D otherVec) {
        // assigns the x,y value of another vector to itself
        this.x = otherVec.x;
        this.y = otherVec.y;
    }

    private Vector2D reduceLength(double length) {
        // Returns a copy of the vector with "length" units subtracted from its total magnitude
        return this.scale((getMagnitude() - length) / getMagnitude());
    }

    private Polygon createArrow(double headSize, Vector2D shiftAmount) {
        Polygon triangle = new Polygon();
        Vector2D tip = this.norm().scale(2 * headSize).scaleCenter(this.reduceLength(2 * headSize).add(shiftAmount));
        Vector2D b1 = this.orthonorm().scale(headSize).scaleCenter(this.reduceLength(2 * headSize).add(shiftAmount));
        Vector2D b2 = this.orthonorm().scale(-headSize).scaleCenter(this.reduceLength(2 * headSize).add(shiftAmount));
        triangle.addPoint((int) tip.x, (int) tip.y);
        triangle.addPoint((int) b1.x, (int) b1.y);
        triangle.addPoint((int) b2.x, (int) b2.y);
        return triangle;
    }

    public Vector2D add(Vector2D otherVector) {
//        Vector2D newVec = new Vector2D(this);
//        newVec.x += otherVector.x;
//        newVec.y += otherVector.y;
        this.x += otherVector.x;
        this.y += otherVector.y;
        return this;
    }

    private Vector2D scaleCenter(Vector2D shiftAmount) {
        // Returns a copy of the vector, shifted and scaled appropriately to be drawn in the center
//        Vector2D newVec = new Vector2D();
//        newVec.x = (this.x + shiftAmount.x) * gridSize + ORIGIN_X;
//        newVec.y = (this.y + shiftAmount.y) * -gridSize + ORIGIN_Y;
        this.x = (this.x + shiftAmount.x) * gridSize + ORIGIN_X;
        this.y = (this.y + shiftAmount.y) * -gridSize + ORIGIN_Y;
        return this;
    }

    private void drawVec(Graphics2D g2, Vector2D shiftAmount, Color color) {
        // Draws an vector given a offset from the origin
        Vector2D startVec = (new Vector2D()).scaleCenter(shiftAmount);
        Vector2D endVec = this.scaleCenter(shiftAmount);
        g2.setColor(color);
        g2.drawLine((int) startVec.x, (int) startVec.y, (int) endVec.x, (int) endVec.y);
    }


    void drawRay(Graphics2D g2, Vector2D shiftAmount, Color color) {
        // Draws the ray of a vector if it were extended across the entire plane
        this.scale(width).drawVec(g2, shiftAmount, color);
        this.scale(-width).drawVec(g2, shiftAmount, color);
    }

    void drawRay(Graphics2D g2, Color color) {
        // Overload for drawRay(Graphics2D, MathBase.Vector2D) which assumes the MathBase.Vector2D to be (0, 0)
        if (offset == null)
            drawRay(g2, new Vector2D(), color);
        else
            drawRay(g2, offset, color);
    }

    private void drawArrow(Graphics2D g2, Vector2D iHat, Vector2D jHat, double headSize, Vector2D shiftAmount) {
        Vector2D screenVector = iHat.scale(x).add(jHat.scale(y));
        Vector2D draw = screenVector.reduceLength(headSize);
        if (draw.getMagnitude() >= 0.00001) {  // avoid weird bugs from small vectors
            draw.drawVec(g2, shiftAmount, color);
            this.triangleTip = screenVector.createArrow(headSize, shiftAmount);
            g2.setColor(color);
            g2.fillPolygon(triangleTip);
        }
    }

    void drawArrow(Graphics2D g2, Vector2D iHat, Vector2D jHat) {
        if (offset == null)
            drawArrow(g2, iHat, jHat, defaultArrowHeadSize * (-Math.exp(-getScreenMagnitude(iHat, jHat)) + 1), new Vector2D());
        else
            drawArrow(g2, iHat, jHat, defaultArrowHeadSize * (-Math.exp(-getScreenMagnitude(iHat, jHat)) + 1), offset);
    }

    public double getVectorX() {
        return x;
    }

    public double getVectorY() {
        return y;
    }

    private double getScreenX(Vector2D iHat, Vector2D jHat) {
        return (this.x * iHat.x + this.y * jHat.x) * gridSize + ORIGIN_X;
    }

    private double getScreenY(Vector2D iHat, Vector2D jHat) {
        return (this.x * iHat.y + this.y * jHat.y) * -gridSize + ORIGIN_Y;
    }

    void setScreenPos(double newX, double newY, Vector2D iHat, Vector2D jHat) {
        if (jHat.x * iHat.y != jHat.y * iHat.x)   // if non-zero determinant (easy case)
            this.y = ((newY - ORIGIN_Y) * iHat.x + (newX - ORIGIN_X) * iHat.y) / (gridSize * (jHat.x * iHat.y - jHat.y * iHat.x));

        //else pass;               // if no x or y components in either basis vector (everything goes to nullspace)

        if (Math.abs(iHat.x) >= 0.01)
            this.x = (newX - ORIGIN_X - this.y * gridSize * jHat.x) / (gridSize * iHat.x);
    }

    public void setColor(Color color) {
        this.color = color;
    }

    public String toString() {
        if (ID != null)
            return "Vector2D([x = " + x + ", y = " + y + "], ID = " + ID + ")";
        else
            return "Vector2D([x = " + x + ", y = " + y + "])";
    }

    Integer getID() {
        return ID;
    }

    void addOffset(Vector2D deltaOffset) {
        if (this.offset == null) {
            this.offset = deltaOffset;
        } else
            this.offset = this.offset.add(deltaOffset);
    }

    Vector2D getOffset() {
        return offset;
    }

    public void setOffset(Vector2D offset) {
        this.offset = offset;
    }

    Vector2D getOffsetSafe() {
        if (offset != null)
            return getOffset();
        else
            return new Vector2D();
    }
}

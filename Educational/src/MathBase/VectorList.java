//----------------------------------------------------------------------------------------|
//  VectorList.java - JComponent extension that allows a list of vectors to be drawn to   |
//  the screen, and provides methods to search for a given vector by its id               |
//----------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                             |
//  Date: 2019-01-15                                                                      |
//----------------------------------------------------------------------------------------|
//  Input: Vector2Ds to add to the list                                                   |
//  Output: Vectors retreived by ID                                                       |
//----------------------------------------------------------------------------------------|
package MathBase;

import javax.swing.*;
import java.awt.*;
import java.util.ArrayList;

public class VectorList extends JComponent {
    private ArrayList<Vector2D> vectors = new ArrayList<>();
    private LinalgGrid gridRef;

    VectorList(LinalgGrid gridRef) {
        this.gridRef = gridRef;
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        for (Vector2D vector : vectors) {
            vector.drawArrow((Graphics2D) g, gridRef.iHatGet(), gridRef.jHatGet());
        }
    }

    private boolean isntUniqueID(Vector2D addVec) {
        for (Vector2D vec : vectors) {
            if (addVec.getID().equals(vec.getID()))
                return true;   // if the ID already occurs somewhere, then inform whomstsoever is trying to add it
            if (vec.getOffset() != null)
                if (addVec.getID().equals(vec.getOffset().getID())) return true;
        }

        if (addVec.getOffset() != null)
            for (Vector2D vec : vectors) {
                if (addVec.getOffset().getID().equals(vec.getID()))
                    return true;   // if the ID already occurs somewhere, then inform whomstsoever is trying to add it
                if (vec.getOffset() != null)
                    if (addVec.getOffset().getID().equals(vec.getOffset().getID())) return true;
            }

        return false;
    }

    void addVector(Vector2D addVec) {
        if (addVec.getID() != null) {
            if (isntUniqueID(addVec))
                throw new ArrayStoreException("You tried to add 2 vectors with the same ID! Here's your list: " + vectors + " and here's the thing you wanted to add: " + addVec);
        }
        vectors.add(addVec);
        repaint();
    }

    Vector2D getArrowByID(int ID) {
        for (Vector2D vec : vectors) {
            if (vec.getID() == ID)
                return vec;
            else if (vec.getOffset() != null) {
                try {
                    if (vec.getOffset().getID() == ID)
                        return vec.getOffset();
                } catch (NullPointerException ignored) {
                }
            }
        }
        return null;
    }

    void scaleVectorByID(int ID, Vector2D newVal) {
        getArrowByID(ID).assign(newVal);
        revalidate();
    }

    void translateVectorByID(int ID, Vector2D newOffset) {
        getArrowByID(ID).addOffset(newOffset);
        revalidate();
    }

    void translateAnimate(TranslateAnimatorTimer tat) {
        tat.setGridRef(gridRef);
        tat.start();
    }

    void scaleAnimate(ScaleAnimatorTimer sat) {
        sat.setGridRef(gridRef);
        sat.setScaleVector(getArrowByID(sat.getID()));
        sat.start();
    }

    void clear() {
        vectors.clear();
    }

    Vector2D trySelect(double mouseX, double mouseY) {
        for (Vector2D arrow : vectors) {
            if (arrow.clicked(mouseX, mouseY)) return arrow;
        }
        return null;
    }

    void removeByID(int ID) {
        for (Vector2D vec : vectors) {
            if (vec.getID() == ID) {
                vectors.remove(vec);
                return;
            }
        }
    }

    public ArrayList<Vector2D> getVectors() {
        return vectors;
    }

    public int length() {
        return vectors.size();
    }


    @Override
    public String toString() {
        return vectors.toString();
    }
}

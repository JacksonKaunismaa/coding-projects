//---------------------------------------------------------------------------------------|
//  ScaleAnimatorThread.java - Given a vector and scalar, it slowly shows the Vector     |
//  scaling its length by that amount, animates the vector by that amount asynchronously |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
//  Input: A Vector, a scalar amount to scale by, an ID for grouping animations          |
//  Output: Visual representation of the vector being scaled by that amount slowly       |
//---------------------------------------------------------------------------------------|
package MathBase;

import TeachPanel.TeachPanel;

import javax.swing.*;
import java.awt.event.ActionListener;

public class ScaleAnimatorTimer {

    private double animateAmount;
    private Vector2D initCopy; // Copies of initial iHat and jHat
    private LinalgGrid gridRef;
    private int ID;
    private Timer timer;

    public ScaleAnimatorTimer(int ID, double scaleAmount, TeachPanel teachPanel) {
        this.ID = ID;
        animateAmount = 0;
        double step = 0.1;

        ActionListener runner = e -> {
            if (animateAmount <= 1.0001) {
                gridRef.scaleByID(ID, initCopy.scale(1 - animateAmount).add(initCopy.scale(scaleAmount * animateAmount)));
                //System.out.println("new vec is " + scaleVector + " group is " + group + " initCopy is " + initCopy);
                gridRef.repaint();
                animateAmount += step;
            } else {
                gridRef.scaleByID(ID, initCopy.scale(1 - animateAmount).add(initCopy.scale(scaleAmount * animateAmount)));
                gridRef.repaint();
                timer.stop();
                teachPanel.enableButtons();
            }
        };

        timer = new Timer(5, runner);
    }

    void start() {
        timer.start();
    }


    void setGridRef(LinalgGrid gridRef) {
        this.gridRef = gridRef;
    }


    void setScaleVector(Vector2D scaleVector) {
        this.initCopy = new Vector2D(scaleVector);
    }


    int getID() {
        return ID;
    }
}

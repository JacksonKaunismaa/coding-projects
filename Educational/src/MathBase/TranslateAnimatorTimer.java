//---------------------------------------------------------------------------------------|
//  TranslateAnimatorThread.java - Given 2 vectors one to animate, one to offset the     |
//  other, shows the first vector moving around the plane until it is offset (which is   |
//  added to any previous offsets that the vector had) by the amount input               |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
//  Input: 2 vectors, one to animate, the other that will be added to it (as offset)     |
//  Output:   Visual representation of the linear transformation slowly being applied by |
////          moving the basis vectors to the desired position and redrawing the grid    |
//---------------------------------------------------------------------------------------|
package MathBase;

import TeachPanel.TeachPanel;

import javax.swing.*;
import java.awt.event.ActionListener;

public class TranslateAnimatorTimer {
    private double animateAmount;
    private LinalgGrid gridRef;
    private Vector2D eventualResult, translateAmount;
    private int ID;
    private Timer timer;

    public TranslateAnimatorTimer(int ID, Vector2D translateAmount, TeachPanel teachPanel) {
        this.ID = ID;
        this.translateAmount = translateAmount;
        animateAmount = 0;
        double step = 0.1;

        ActionListener runner = e -> {
            if (animateAmount <= 1.0001) {
                gridRef.translateByID(ID, gridRef.iHatGet().scale(step * translateAmount.getVectorX()).add(gridRef.jHatGet().scale(step * translateAmount.getVectorY())));
                gridRef.repaint();
                animateAmount += step;
            } else {
                gridRef.setTranslateByID(ID, gridRef.iHatGet().scale(eventualResult.getVectorX()).add(gridRef.jHatGet().scale(eventualResult.getVectorY())));
                gridRef.repaint();
                timer.stop();
                teachPanel.enableButtons();
            }
        };

        timer = new Timer(20, runner);
    }

    void start() {
        eventualResult = gridRef.arrowList.getArrowByID(ID).getOffsetSafe().scale(1).add(translateAmount);
        timer.start();
    }

    void setGridRef(LinalgGrid gridRef) {
        this.gridRef = gridRef;
    }

    public int getID() {
        return ID;
    }
}

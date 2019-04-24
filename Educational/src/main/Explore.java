//---------------------------------------------------------------------------------------|
//  Explore.java - This is the JPanel for the "explore" mode where the user can add      |
//                 vectors to a grid, as well as apply linear transformations to the grid|
//                 and the vectors, to see what happens.                                 |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
//  Input: Mouse position and right clicks for adding vectors, slider positions to change|
//         values for a linear transformation that are applied by clicking a button      |
//  Output: Visual representation of vectors on a grid, and the effect of linear         |
//          transformations on these vectors and the grid.                               |
//---------------------------------------------------------------------------------------|
package main;

import MathBase.LinalgGrid;
import MathBase.Vector2D;
import TransformPanel.TransformEvent;
import TransformPanel.TransformEventListener;
import TransformPanel.TransformPanel;
import TransformPanel.EigenEventListener;

import javax.swing.event.EventListenerList;
import java.awt.*;

public class Explore extends ExitPanel {
    private EventListenerList listenerList = new EventListenerList();

    Explore() {
        setLayout(new BorderLayout());

        // define components of the panel
        // grid to add vectors (center)
        LinalgGrid grid = new LinalgGrid(true, true, false);

        // panel on the left to specify a linear transformation
        TransformPanel tp = new TransformPanel(true);
        tp.addTransformListener(new TransformEventListener() {
            public void applyTransform(TransformEvent evt) {
                grid.retransform(evt.iHatGet(), evt.jHatGet());
            }
        });

        tp.addEigenListener(new EigenEventListener() {
            public void sendEigen(TransformEvent evt){
                grid.addEigen(evt.iHatGet(), evt.jHatGet());
            }
        });

        tp.setGridRef(grid);    // hacky stuff please ignore
        tp.setExploreRef(this);

        // add components to the panel
        add(grid, BorderLayout.CENTER);
        add(tp, BorderLayout.WEST);
    }

    // boiler plate code (implementation is always the same) for listening when "Quit" is pressed to return to the main menu
    protected void addExitListener(ExitEventListener listener) {
        listenerList.add(ExitEventListener.class, listener);
    }
    // more boiler plate code
    public void fireExitEvent() {
        Object[] listeners = listenerList.getListenerList(); // get all listeners
        for (int i = 0; i < listeners.length; i += 2) // step by 2 at a time because listenerList is like classType1, listener1, classType2, listener2, classType3, listener3,
        { // thus all the even numbered indices are just the classes, and the odd numbered ones are the actual listeners
            if (listeners[i] == ExitEventListener.class) { // if the listener happens to be a ExitEventListener, we can now fire exitedOrFinished (equivalent to "actionPerformed");
                ((ExitEventListener) listeners[i + 1]).exitedOrFinished();
            }
        }
    }
}

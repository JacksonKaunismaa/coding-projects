//---------------------------------------------------------------------------------------|
//  ExitPanel.java - JPanel super class used for all menus that allows exit listeners    |
//                   through which you can exit and return to a previous menu            |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|

package main;

import javax.swing.*;
import javax.swing.event.EventListenerList;

public class ExitPanel extends JPanel {
    // listenerList used when you want to add a listener to the panel for when the user clicks "quit" or "exit" or something
    private EventListenerList listenerList = new EventListenerList();

    // boiler plate code for exiting a menu
    protected void addExitListener(ExitEventListener listener) {
        listenerList.add(ExitEventListener.class, listener);
    }

    protected void fireExitEvent() {
        Object[] listeners = listenerList.getListenerList(); // get all listeners
        for (int i = 0; i < listeners.length; i += 2) // step by 2 at a time because listenerList is like classType1, listener1, classType2, listener2, classType3, listener3,
        { // thus all the even numbered indices are just the classes, and the odd numbered ones are the actual listeners
            if (listeners[i] == ExitEventListener.class) { // if the listener happens to be a ColorPanelListener, we can now fire colorChanged (equivalent to "actionPerformed");
                ((ExitEventListener) listeners[i + 1]).exitedOrFinished();
            }
        }
    }
}

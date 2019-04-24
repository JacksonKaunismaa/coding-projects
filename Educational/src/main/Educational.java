//---------------------------------------------------------------------------------------|
//  Educational.java - Main method that holds the main JFrame and handles the closing    |
//                     operations. It also sets the size of the main frame,  but overall |
//                     is mostly just a container for everything else.                   |
//                     update                                                            |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
package main;

import MathBase.Vector2D;

import javax.swing.*;

public class Educational {
    public static void main(String[] args) {

        SwingUtilities.invokeLater(() -> {
            MainFrame frame = new MainFrame();
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);  // exit when the user presses the close button in the top right
            frame.setExtendedState(JFrame.MAXIMIZED_BOTH);
            frame.setVisible(true);
        });
    }

}

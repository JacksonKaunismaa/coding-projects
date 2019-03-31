//---------------------------------------------------------------------------------------|
//  LessonSelect.java - Main menu for selecting the 3 different modes to choose          |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
//  Input: A selection choice for the main menu of one of the 3 modes                    |
//  Output: The appropriate type of mode screen is displayed                             |
//---------------------------------------------------------------------------------------|
package main;

import javax.swing.*;
import java.awt.*;

class MainFrame extends JFrame {
    MainFrame() {
        // set the title on top of the frame
        super("Linear Algebra Tool");

        // stuff for adding things to the main menu and changing screens
        Container c = getContentPane();
        JPanel screens = new JPanel();
        CardLayout cardLayout = new CardLayout();
        screens.setLayout(cardLayout);

        // screen for "exploration" mode (see Explore.java)
        Explore explore = new Explore();
        explore.addExitListener(new ExitEventListener() {  // allows for exiting back to the main menu from exploration mode
            @Override
            public void exitedOrFinished() {
                cardLayout.show(screens, "main");
            }
        });

        // screen for "testing" mode (see TestSelect.java)
        TestSelect testSelect = new TestSelect();
        testSelect.addExitListener(new ExitEventListener() {  // allows for exiting back to the main menu from testing mode
            @Override
            public void exitedOrFinished() {
                cardLayout.show(screens, "main");
            }
        });

        // screen for "learning" mode (see LessonSelect.java)
        LessonSelect lessonSelect = new LessonSelect();
        lessonSelect.addExitListener(new ExitEventListener() {  // allows for exiting back to the main menu from lesson mode
            @Override
            public void exitedOrFinished() {
                cardLayout.show(screens, "main");
            }
        });

        // panel to allow for navigation to the different modes (actual main menu)
        JPanel mainMenu = new JPanel();
        JButton exploreBtn, testSelectBtn, lessonSelectBtn;
        GridBagLayout gb = new GridBagLayout();
        GridBagConstraints gc = new GridBagConstraints();
        mainMenu.setLayout(gb);

        // buttons for each mode
        exploreBtn = new JButton("Explore");
        exploreBtn.addActionListener(e -> cardLayout.show(screens, "explore"));

        lessonSelectBtn = new JButton("Learn");
        lessonSelectBtn.addActionListener(e -> cardLayout.show(screens, "learn"));

        testSelectBtn = new JButton("Test");
        testSelectBtn.addActionListener(e -> cardLayout.show(screens, "test"));

        JLabel title = new JLabel("Linear Algebra Tool");
        title.setFont(new Font(Font.MONOSPACED, Font.BOLD, 40));

        gc.ipady = 50;
        gc.ipadx = 200;
        gc.insets = new Insets(30, 0, 30, 0);
        gc.anchor = GridBagConstraints.CENTER;
        gc.fill = GridBagConstraints.BOTH;

        gc.gridx = 0;
        gc.gridy = 0;
        gb.setConstraints(title, gc);
        mainMenu.add(title);

        gc.gridx = 0;
        gc.gridy = 1;
        gb.setConstraints(lessonSelectBtn, gc);
        mainMenu.add(lessonSelectBtn);

        gc.gridx = 0;
        gc.gridy = 2;
        gb.setConstraints(testSelectBtn, gc);
        mainMenu.add(testSelectBtn);

        gc.gridx = 0;
        gc.gridy = 3;
        gb.setConstraints(exploreBtn, gc);
        mainMenu.add(exploreBtn);

        // main menu screen cards
        screens.add(explore, "explore");
        screens.add(mainMenu, "main");
        screens.add(lessonSelect, "learn");
        screens.add(testSelect, "test");
        cardLayout.show(screens, "main");
        c.add(screens);
    }
}

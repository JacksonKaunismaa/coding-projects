//---------------------------------------------------------------------------------------|
//  LessonSelect.java - Menu for selecting a lesson to study from the folder "Teach_Text"|
//                      and it inherits from ExitPanel so that the lesson can be exited  |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
//  Input: A bunch of text files to be parsed into actual lessons that can be navigated. |
//         User input by choosing 1 of these text files, or back to return to main menu  |
//  Output: The lesson text files properly formatted, including animations, text, vectors|
//          and linear transformations.                                                  |
//---------------------------------------------------------------------------------------|
package main;

import MathBase.LinalgGrid;
import TeachPanel.TeachPanel;
import TransformPanel.TransformEvent;
import TransformPanel.TransformEventListener;
import TransformPanel.TransformPanel;

import javax.swing.*;
import java.awt.*;
import java.io.File;

class LessonSelect extends ExitPanel {
    // selectScreen = menu to choose a lesson, lessonScreen = after choosing a lesson, display it, and cards = container for both
    private JPanel selectScreen, lessonScreen, cards;
    // cardLayout allows you to easily hide and show the menu to select a lesson
    private CardLayout cardLayout;

    LessonSelect() {
        setLayout(new BorderLayout());

        // container for panels
        cards = new JPanel();
        cardLayout = new CardLayout();
        cards.setLayout(cardLayout);

        // screens that go inside the cardLayout
        selectScreen = new JPanel();
        selectScreen.setLayout(new FlowLayout());
        JButton btn = new JButton("Quit");   // create new button
        btn.addActionListener(e -> {
            fireExitEvent();
        });
        selectScreen.add(btn);
        addAllButtons();   // add buttons to select lessons

        lessonScreen = new JPanel();
        lessonScreen.setLayout(new BorderLayout());

        cards.add(selectScreen, "select");
        cards.add(lessonScreen, "lesson");
        cardLayout.show(cards, "select");
        add(cards, BorderLayout.CENTER);
    }

    // when a lesson is chosen, generate the screen for the user to actually view the lesson
    private void generateLessonScreen(String name) {
        lessonScreen.removeAll();   // clear the previous lesson that user displayed
        TeachPanel tp = new TeachPanel(name);   // panel that goes on the right and displays the info of the lesson file
        LinalgGrid grid = new LinalgGrid(      // grid for demonstrating visual animations and intuitions
                tp.getHeaderInfo().findBasisChange()[0],
                tp.getHeaderInfo().findBasisChange()[1],
                tp.getHeaderInfo().basisVisible(),
                tp.getHeaderInfo().isTransformPanel(),
                true,
                tp.getHeaderInfo().addingAllowed());
        tp.setGridReference(grid);
        tp.addExitListener(new ExitEventListener() {   // if clicked exit, return to button screen
            @Override
            public void exitedOrFinished() {
                cardLayout.show(cards, "select");
            }
        });
        // part of the lesson parsing, whether or not you want the user to be able to input their own transformations
        // boiler plate code for communication between the left panel (for specifying transformations) and the grid
        if (tp.getHeaderInfo().isTransformPanel()) {
            TransformPanel transformPanel = new TransformPanel(tp.getHeaderInfo().findBasisChange()[0], tp.getHeaderInfo().findBasisChange()[1]);
            transformPanel.addTransformListener(new TransformEventListener() {
                public void applyTransform(TransformEvent evt) {
                    grid.retransform(evt.iHatGet(), evt.jHatGet());
                }
            });
            lessonScreen.add(transformPanel, BorderLayout.WEST);

        }
        // add everything to the lesson screen
        lessonScreen.add(grid, BorderLayout.CENTER);
        lessonScreen.add(tp, BorderLayout.EAST);
    }


    private void addButton(String name) {
        JButton btn = new JButton(name);   // create new button
        btn.addActionListener(e -> {
            generateLessonScreen(name);
            cardLayout.show(cards, "lesson");   // show the lesson when the button is clicked (lesson is selected)
        });
        selectScreen.add(btn);
    }

    // reads all the files in the "Teach_Text" directory and tries to turn them into lessons and adds a button for each file
    private void addAllButtons() {
        File learnDir = new File("Teach_Text");
        File[] learnFiles = learnDir.listFiles();

        assert learnFiles != null;
        for (File file : learnFiles) {
            addButton(file.getName());
        }
    }

}


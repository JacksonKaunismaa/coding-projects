//---------------------------------------------------------------------------------------|
//  TestSelect.java - Menu for selecting a test from the folder "Question_Text", and it  |
//                     inherits from ExitPanel so that the test can be exited            |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
//  Input: A bunch of text files to be parsed into actual tests that can be navigated.   |
//         User input by choosing 1 of these text files, or back to return to main menu  |
//  Output: The test text files properly formatted, including animations, text, vectors  |
//          and linear transformations. Also it saves the test/question file with the    |
//          update score which is technically an output                                  |
//---------------------------------------------------------------------------------------|
package main;

import MathBase.LinalgGrid;
import QuestionPanel.*;
import TransformPanel.TransformEvent;
import TransformPanel.TransformEventListener;
import TransformPanel.TransformPanel;

import javax.swing.*;
import java.awt.*;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;

class TestSelect extends ExitPanel {
    // testSelect = menu for selecting a test (only some are enabled), testScreen = ask the user the questions, cards = container to hide/show the 2 menus
    private JPanel testSelect, testScreen, cards;
    private CardLayout cardLayout;

    // used when a test is successfully completed to allow the next lesson to be accessed
    private ArrayList<JButton> buttonArrayList;

    TestSelect() {
        setLayout(new BorderLayout());

        // container for 2 menus
        cards = new JPanel();
        cardLayout = new CardLayout();
        cards.setLayout(cardLayout);

        // menu for choosing a test
        testSelect = new JPanel();
        testSelect.setLayout(new FlowLayout());
        JButton btn = new JButton("Quit");   // create new button
        btn.addActionListener(e -> {
            fireExitEvent();
        });
        testSelect.add(btn);
        addAllButtons();

        // menu for navigating the questions
        testScreen = new JPanel();
        testScreen.setLayout(new BorderLayout());

        // add stuff to the panel
        cards.add(testSelect, "select");
        cards.add(testScreen, "test");
        cardLayout.show(cards, "select");
        add(cards, BorderLayout.CENTER);
    }

    private void generateTestingScreen(String name, int idx) {
        testScreen.removeAll();   // clear the testScreen so its ready to have new elements added
        QuestionPanel qp = new QuestionPanel(name);   // add right panel to ask questions/submit answers
        LinalgGrid grid = new LinalgGrid(qp.getHeaderInfo().isTransformPanel());   // for animations/illustration of problems
        qp.setGridRef(grid);        // hacky
        qp.addExitListener(new QuestionPanelEventListener() {
            @Override
            public void exitUpdate(QuestionExitEvent evt) {   // if clicked exit, return to button screen
                qp.save();
                if (evt.testCompleted()) {
                    try {
                        JButton nextBtn = buttonArrayList.get(idx + 1);  // if they got a perfect score after having exited the test
                        nextBtn.setEnabled(true);                        // then make the next test be available
                        nextBtn.setOpaque(true);
                    } catch (IndexOutOfBoundsException ignored) {}
                }
                cardLayout.show(cards, "select");  // return to testSelect menu
            }
        });
        if (qp.getHeaderInfo().isTransformPanel()) {  // see teachInfo panel
            TransformPanel transformPanel = new TransformPanel(qp.getHeaderInfo().findBasisChange()[0], qp.getHeaderInfo().findBasisChange()[1]);
            transformPanel.addTransformListener(new TransformEventListener() {
                public void applyTransform(TransformEvent evt) {
                    grid.retransform(evt.iHatGet(), evt.jHatGet());
                }
            });
            testScreen.add(transformPanel, BorderLayout.WEST);

        }
        testScreen.add(grid, BorderLayout.CENTER);
        testScreen.add(qp, BorderLayout.EAST);
    }

    private void addButton(String name, boolean unlocked, int idx) {
        JButton btn = new JButton(name);   // create new button
        if (!unlocked) {
            btn.setOpaque(false);
            btn.setEnabled(false);
        }
        btn.addActionListener(e -> {
            generateTestingScreen(name, idx);
            cardLayout.show(cards, "test");
        });
        testSelect.add(btn);
        buttonArrayList.add(btn);
    }

    // add buttons to select a file from the test/question directory "Question_Text," checking for which tests should be enabled
    private void addAllButtons() {
        File learnDir = new File("Question_Text");
        File[] learnFiles = learnDir.listFiles();
        int idx = 0;
        buttonArrayList = new ArrayList<>();
        assert learnFiles != null;
        boolean unlocked = true;

        for (File file : learnFiles) {
            addButton(file.getName(), unlocked, idx);
            if (unlocked)
                try {   // if the previous test doesn't have a perfect score, then disable the subsequent lessons, so they have to go through them in order
                    QuestionReader qr = new QuestionReader("Question_Text", file.getName());   // open up the file and see if the user has a perfect score (has passed the test before to see
                    if (new Question(qr.getHeaderInfo()).getScore() != qr.getLength())                    // if they have access to the next test
                        unlocked = false;
                } catch (IOException e) {
                    e.printStackTrace();
                }
            idx++;
        }
    }
}


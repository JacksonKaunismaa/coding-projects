//---------------------------------------------------------------------------------------|
//  QuestionPanel.java - Panel that allows the user to do tests and make sure they       |
//  understand topics before being allowed to move on. It provides navigation from       |
//  question to question, and tracks score and what not                                  |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
//  Input: Answers and navigation clicks                                                 |
//  Output: Scores, updated question/test files, user messages tracking progress         |
//---------------------------------------------------------------------------------------|
package QuestionPanel;

import MathBase.LinalgGrid;
import MathBase.Vector2D;

import javax.sound.sampled.LineUnavailableException;
import javax.sound.sampled.UnsupportedAudioFileException;
import javax.swing.*;
import javax.swing.event.EventListenerList;
import java.awt.*;
import java.io.IOException;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class QuestionPanel extends JPanel {
    private final int FONT_SIZE = 15;
    private EventListenerList listenerList = new EventListenerList();
    private QuestionReader questionReader;
    private Question headerInfo, question;
    private Font font;
    private JLabel display, correctLabel;
    private JButton submit, reset, exit;
    private LinalgGrid gridRef;
    private int score = 0;
    private JPanel flippable;
    private CardLayout cardLayout;
    private JTextArea textInput;
    private SoundPlayer soundPlayer = new SoundPlayer();

    public QuestionPanel(String filename) {
        try {
            questionReader = new QuestionReader("Question_Text", filename);
        } catch (IOException e) {
            e.printStackTrace();
        }
        headerInfo = new Question(questionReader.getHeaderInfo());
        question = questionReader.getNext();

        Dimension size = new Dimension(400, 800);
        setPreferredSize(size);

        GridBagLayout gb = new GridBagLayout();
        GridBagConstraints gc = new GridBagConstraints();
        setLayout(gb);
        setBorder(BorderFactory.createTitledBorder(headerInfo.findDisplayInfo()));
        font = new Font(Font.MONOSPACED, Font.BOLD, FONT_SIZE);

        display = new JLabel();
        display.setFont(font);
        display.setText(question.getQuestionDisplay());
        display.setMinimumSize(new Dimension(380, 500));
        display.setForeground(new Color(0, 0, 0));


        correctLabel = new JLabel(String.format("Question 1/%d", questionReader.getLength()));
        correctLabel.setFont(font);
        correctLabel.setForeground(new Color(0, 0, 0));


        submit = new JButton("Submit");
        submit.addActionListener(e -> {
            switch (submit.getText()) {
                case "Submit":
                    try {
                        answerSubmitted();
                    } catch (UnsupportedAudioFileException | IOException | LineUnavailableException e1) {
                        e1.printStackTrace();
                    }
                    break;
                case "Continue":
                    try {
                        redisplayQuestion();
                    } catch (UnsupportedAudioFileException | IOException | LineUnavailableException e1) {
                        e1.printStackTrace();
                    }
                    break;
                case "Return":
                    fireExitEvent(new QuestionExitEvent(this, score == questionReader.getLength()));
                    break;
            }
        });

        reset = new JButton("Reset");
        reset.addActionListener(e -> {
            resetGrid();
        });

        textInput = new JTextArea();

        flippable = new JPanel();
        cardLayout = new CardLayout();
        flippable.setLayout(cardLayout);
        flippable.add(reset, "vectors");
        flippable.add(textInput, "text");
        cardLayout.show(flippable, question.getType());

        exit = new JButton("Quit");
        exit.addActionListener(e -> {
            if (submit.getText().equals("Return"))
                fireExitEvent(new QuestionExitEvent(this, score == questionReader.getLength()));
            else {
                try {
                    showQuitScreen();
                } catch (UnsupportedAudioFileException | IOException | LineUnavailableException e1) {
                    e1.printStackTrace();
                }
            }
        });


        gc.fill = GridBagConstraints.BOTH;
        gc.anchor = GridBagConstraints.CENTER;

        gc.gridwidth = 3;
        gc.gridx = 0;
        gc.gridy = 0;
        gb.setConstraints(correctLabel, gc);
        add(correctLabel);

        gc.gridwidth = 3;
        gc.gridx = 0;
        gc.gridy = 1;
        gb.setConstraints(display, gc);
        add(display);

        gc.gridheight = 1;
        gc.gridwidth = 1;

        gc.gridx = 0;
        gc.gridy = 2;
        gb.setConstraints(exit, gc);
        add(exit);

        gc.gridx = 1;
        gc.gridy = 2;
        gb.setConstraints(flippable, gc);
        add(flippable);

        gc.gridx = 2;
        gc.gridy = 2;
        gb.setConstraints(submit, gc);
        add(submit);
    }

    public Question getHeaderInfo() {
        return headerInfo;
    }

    public void setGridRef(LinalgGrid gridRef) {
        this.gridRef = gridRef;
        resetGrid();
    }

    private void resetGrid() {
        gridRef.clearVectors();
        gridRef.setDrawBasis(question.basisVisible());
        gridRef.setAddAllowed(question.addingAllowed());
        Vector2D[] newBasis = question.findBasisChange();
        if (newBasis[0] != null || newBasis[1] != null)   // if a change detected, then change the basis
            gridRef.retransform(newBasis[0], newBasis[1]);

        for (Vector2D vector : question.getVectorInfo()) {
            gridRef.addVector(vector);
        }
    }

    public void addExitListener(QuestionPanelEventListener listener) {
        listenerList.add(QuestionPanelEventListener.class, listener);
    }

    private void fireExitEvent(QuestionExitEvent evt) {
        Object[] listeners = listenerList.getListenerList(); // get all listeners
        for (int i = 0; i < listeners.length; i += 2) // step by 2 at a time because listenerList is like classType1, listener1, classType2, listener2, classType3, listener3,
        { // thus all the even numbered indices are just the classes, and the odd numbered ones are the actual listeners
            if (listeners[i] == QuestionPanelEventListener.class) { // if the listener happens to be a ColorPanelListener, we can now fire colorChanged (equivalent to "actionPerformed");
                ((QuestionPanelEventListener) listeners[i + 1]).exitUpdate(evt);
            }
        }
    }

    private void showQuitScreen() throws UnsupportedAudioFileException, IOException, LineUnavailableException {
        correctLabel.setText("");
        if (score!=questionReader.getLength()) {
            soundPlayer.playSound("fail.wav");
            display.setText("<html>Congratulations, your final score was " + score + " out of a total possible score of "
                    + questionReader.getLength() + ", or " + (100. * (double) score / (double) questionReader.getLength()) +
                    "%. You  will need a score of 100% to get the ability to advance to the next test! Good luck!" + "</html>");
        }
        else {
            soundPlayer.playSound("win.wav");
            display.setText("<html>Congratulations, your final score was " + score + " out of a total possible score of "
                    + questionReader.getLength() + ", or " + (100. * (double) score / (double) questionReader.getLength()) +
                    "%. You can now move on to the next lesson! Good luck!" + "</html>");
        }
        submit.setText("Return");
    }

    private void redisplayQuestion() throws UnsupportedAudioFileException, IOException, LineUnavailableException {
        if (questionReader.getIter() != questionReader.getLength() - 1) {
            question = questionReader.getNext();
            submit.setText("Submit");
            reset.setEnabled(true);
            reset.setOpaque(true);
            resetGrid();
            display.setText(question.formatQuestion());
            textInput.setText("");
            correctLabel.setText(String.format("Question %d/%d", questionReader.getIter() + 1, questionReader.getLength()));
            this.setBackground(new Color(214, 214, 214));
            cardLayout.show(flippable, question.getType());
        } else
            showQuitScreen();
    }

    public void save() {
        questionReader.resave(score);
    }

    private void displayAnswer(boolean wasCorrect, ArrayList<Double> guess) throws UnsupportedAudioFileException, IOException, LineUnavailableException {
        submit.setText("Continue");
        reset.setEnabled(false);
        reset.setOpaque(false);
        display.setText(question.getAnswerDisplay(guess));
        if (wasCorrect) {
            this.setBackground(new Color(0, 167, 3));
            soundPlayer.playSound("correct.wav");
            correctLabel.setText("<html>Correct! " + score + " out of total possible score up to this point of " + (questionReader.getIter() + 1) + "</html>");
        }
        else {
            soundPlayer.playSound("wrong.wav");
            this.setBackground(new Color(186, 7, 0));
            correctLabel.setText("<html>Wrong! " + score + " out of total possible score up to this point of " + (questionReader.getIter() + 1) + "</html>");
        }
    }

    private void answerSubmitted() throws UnsupportedAudioFileException, IOException, LineUnavailableException {
        String type = question.getType();
        ArrayList<Double> guess = new ArrayList<>();
        switch (type) {
            case "vectors":
                for (Vector2D drag : gridRef.getDraggable()) {
                    guess.add(drag.getVectorX());
                    guess.add(drag.getVectorY());
                }
                break;
            case "text":
                Matcher doubleGetter = Pattern.compile("([^,]+)").matcher(textInput.getText());
                while (doubleGetter.find()) {
                    try {
                        guess.add(Double.parseDouble(doubleGetter.group(1)));
                    } catch (NumberFormatException ignored) {
                        textInput.setText("There was an error in parsing your answer");
                    }
                }
                break;
            case "transform":
                break;
            default:
                System.out.println("Uh oh");
                return;
        }

        if (question.checkAnswer(guess)) {
            score += 1;
            displayAnswer(true, guess);
        } else {
            displayAnswer(false, guess);
        }

    }
}

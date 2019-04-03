//---------------------------------------------------------------------------------------|
//  TeachPanel.java - Panel that allows the user to do browse lessons and learn and      |
//  understand topics before doing the tests. It provides navigation from page to page of|
// text, and does animations on the grid                                                 |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|

package TeachPanel;

import MathBase.LinalgGrid;
import MathBase.ScaleAnimatorTimer;
import MathBase.TranslateAnimatorTimer;
import MathBase.Vector2D;
import main.ExitPanel;

import javax.swing.*;
import javax.swing.event.EventListenerList;
import java.awt.*;
import java.io.IOException;

import static TransformPanel.TransformPanel.FONT_SIZE;

public class TeachPanel extends ExitPanel {
    private TeachInfo teachInfo, headerInfo;
    private TeachReader teachReader;
    private Font font;
    private JLabel display, title;
    private JButton next, back;
    private LinalgGrid gridReference;


    public TeachPanel(String filename) {
        try {
            teachReader = new TeachReader("Teach_Text", filename);
        } catch (IOException e) {
            e.printStackTrace();
        }
        headerInfo = new TeachInfo(teachReader.getHeaderInfo());
        teachInfo = teachReader.getNext();
        Dimension size = new Dimension(400, 800);
        setPreferredSize(size);

        GridBagLayout gb = new GridBagLayout();
        GridBagConstraints gc = new GridBagConstraints();
        setLayout(gb);
        setBorder(BorderFactory.createTitledBorder(headerInfo.findDisplayInfo()));
        font = new Font(Font.MONOSPACED, Font.BOLD, FONT_SIZE);

        display = new JLabel();
        display.setFont(font);
        display.setText(teachInfo.findDisplayInfo());
        display.setMinimumSize(new Dimension(400, 500));

        next = new JButton("Next");
        next.addActionListener(e -> {
            teachInfo = teachReader.getNext();
            updateButtons();
            updatePanel(true);
        });

        back = new JButton("Return to lesson select");
        back.addActionListener(e -> {
            if (teachReader.getIter() == 0)
                fireExitEvent();
            teachInfo = teachReader.getPrevious();
            updateButtons();
            updatePanel(false);
        });


        gc.fill = GridBagConstraints.BOTH;
        gc.anchor = GridBagConstraints.CENTER;
        gc.gridx = 0;
        gc.gridy = 0;
        gc.gridwidth = 2;
        gb.setConstraints(display, gc);
        add(display);

        gc.gridheight = 1;
        gc.gridwidth = 1;
        gc.gridx = 0;
        gc.gridy = 1;
        gb.setConstraints(back, gc);
        add(back);

        gc.gridx = 1;
        gc.gridy = 1;
        gb.setConstraints(next, gc);
        add(next);
    }

    public void setGridReference(LinalgGrid gridReference) {
        this.gridReference = gridReference;
    }

    public void disableButtons() {
        disableButton(next);
        disableButton(back);
    }

    public void enableButtons() {
        enableButton(next);
        enableButton(back);
    }

    private void updatePanel(boolean forwardsPass) {
        disableButtons();
        repaint();
        display.setText(teachInfo.findDisplayInfo());
        if (forwardsPass)
            for (Vector2D vector : teachInfo.getVectorInfo()) {
                gridReference.addVector(vector);
            }

        Vector2D[] newBasis = teachInfo.findBasisChange();
        if (newBasis[0] != null || newBasis[1] != null)   // if a change detected, then change the basis
            gridReference.retransform(newBasis[0], newBasis[1]);
        teachInfo.clearVectors();

        for (ScaleAnimatorTimer scaleAnimation : teachInfo.getScaling(this)) {
            disableButtons();
            gridReference.scaleAnimate(scaleAnimation);
        }

        for (TranslateAnimatorTimer translateAnimation : teachInfo.getTranslations()) {
            disableButtons();
            gridReference.translateAnimate(translateAnimation);
        }

        for (Integer removeID : teachInfo.getRemove()) {
            gridReference.removeByID(removeID);
        }
        if (teachInfo.getTranslations().size() + teachInfo.getScaling(this).size() == 0) enableButtons();
        teachInfo.clearAnimations();
    }

    private void disableButton(JButton btn) {
        btn.setEnabled(false);
        btn.setOpaque(false);
    }

    private void enableButton(JButton btn) {
        btn.setEnabled(true);
        btn.setOpaque(true);
    }

    private void updateButtons() {
        if (teachReader.getIter() == teachReader.getLength() - 2 || teachReader.getIter() == teachReader.getLength() - 1) {   // if one before the end
            if (next.getText().equals("Finish"))
                fireExitEvent();
            next.setText("Finish");
            back.setText("Back");
        } else if (teachReader.getIter() == 0) {    // if at the very beginning
            next.setText("Next");
            back.setText("Return to lesson select");
        } else {    // if anywhere else
            next.setText("Next");
            back.setText("Back");
        }
    }

    public TeachInfo getHeaderInfo() {
        return headerInfo;
    }
}

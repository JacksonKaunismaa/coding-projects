//---------------------------------------------------------------------------------------|
//  MatrixDisplay.java - Panel that displays a matrix properly, showing the user the     |
//  current value of the transformation matrix that can be applied by clicking "Apply"   |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
//  Input: Integer values from sliders (user set)                                        |
//  Output: Matrix format display for slider values, scaled into appropriate range       |
//---------------------------------------------------------------------------------------|
package MathBase;

import javax.swing.*;
import java.awt.*;

public class MatrixDisplay extends JPanel {
    private JLabel a11, a12, a21, a22;
    private int left, top, right, bottom;

    public MatrixDisplay(Double a11Start, Double a12Start, Double a21Start, Double a22Start, Font font) {
//        Dimension size = getPreferredSize();
//        size.width = 100;
//        setPreferredSize(size);

        GridBagLayout gb = new GridBagLayout();
        GridBagConstraints gc = new GridBagConstraints();
        setLayout(gb);
        a11 = new JLabel(a11Start.toString());
        a12 = new JLabel(a12Start.toString());
        a21 = new JLabel(a21Start.toString());
        a22 = new JLabel(a22Start.toString());
        a11.setFont(font);
        a12.setFont(font);
        a21.setFont(font);
        a22.setFont(font);

        gc.ipady = 25;
        gc.ipadx = 35;
        //gc.insets = new Insets(5, 0, 7, 0);

        gc.gridx = 0;
        gc.gridy = 0;
        gb.setConstraints(a11, gc);
        add(a11);

        gc.gridx = 0;
        gc.gridy = 1;
        gb.setConstraints(a21, gc);
        add(a21);

        gc.gridx = 1;
        gc.gridy = 0;
        gb.setConstraints(a12, gc);
        add(a12);

        gc.gridx = 1;
        gc.gridy = 1;
        gb.setConstraints(a22, gc);
        add(a22);
        Dimension size = getPreferredSize();
        this.left = -font.getSize();
        this.right = size.width + font.getSize();
        this.top = 2;
        this.bottom = size.height - 2;
    }

    public void setBorders(int shiftRight) {
        this.left += shiftRight;
        this.right += shiftRight;
    }

    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setColor(Color.black);
        g2.setStroke(new BasicStroke(3));
        g2.drawLine(left, top, left, bottom);
        g2.drawLine(right, top, right, bottom);
        g2.drawLine(left, top, left + 10, top);
        g2.drawLine(left, bottom, left + 10, bottom);
        g2.drawLine(right, top, right - 10, top);
        g2.drawLine(right, bottom, right - 10, bottom);
    }

    private void updateMatrix(Vector2D iHatNew, Vector2D jHatNew) {
        a11.setText(((Double) iHatNew.getVectorX()).toString());
        a12.setText(((Double) jHatNew.getVectorX()).toString());
        a21.setText(((Double) iHatNew.getVectorY()).toString());
        a22.setText(((Double) jHatNew.getVectorY()).toString());
    }

    public void updateMatrix(double a11, double a12, double a21, double a22) {
        updateMatrix(new Vector2D(a11, a21), new Vector2D(a12, a22));
    }
}

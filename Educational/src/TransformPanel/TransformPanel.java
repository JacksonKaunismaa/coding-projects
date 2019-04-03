package TransformPanel;

import MathBase.LinalgGrid;
import MathBase.MatrixDisplay;
import MathBase.Vector2D;
import main.Explore;

import javax.swing.*;
import javax.swing.event.EventListenerList;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class TransformPanel extends JPanel {

    public static final int FONT_SIZE = 25;
    private static final int SLIDER_OPTIONS = 50;
    static final double SLIDER_SCALE = (double) SLIDER_OPTIONS / 10.;
    private EventListenerList listenerList = new EventListenerList();
    private JSlider a11, a12, a21, a22;
    private MatrixDisplay matrixDisplay;
    private LinalgGrid gridRef;
    private Explore exploreRef;

    public TransformPanel(boolean special) {
        this(new Vector2D(1, 0), new Vector2D(0, 1), special);
    }

    public TransformPanel(Vector2D iHatInit, Vector2D jHatInit) {
        this(iHatInit, jHatInit, false);
    }

    private TransformPanel(Vector2D iHatInit, Vector2D jHatInit, boolean special) {
        Dimension size = getPreferredSize();
        size.width = 400;
        size.height = 400;
        setPreferredSize(size);

        GridBagLayout gb = new GridBagLayout();
        GridBagConstraints gc = new GridBagConstraints();
        setLayout(gb);
        setBorder(BorderFactory.createBevelBorder(0));
        Font font = new Font(Font.MONOSPACED, Font.BOLD, FONT_SIZE);

        a11 = addSlider((int) (iHatInit.getVectorX() * SLIDER_SCALE));
        a12 = addSlider((int) (jHatInit.getVectorX() * SLIDER_SCALE));
        a21 = addSlider((int) (iHatInit.getVectorY() * SLIDER_SCALE));
        a22 = addSlider((int) (jHatInit.getVectorY() * SLIDER_SCALE));

        JButton transform = new JButton("Apply transformation");
        transform.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                fireTransformEvent(new TransformEvent(this, a11.getValue(), a12.getValue(), a21.getValue(), a22.getValue()));
            }
        });

        JButton identity = new JButton("Reset");
        identity.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                a11.setValue((int) (iHatInit.getVectorX() * SLIDER_SCALE));
                a12.setValue((int) (jHatInit.getVectorX() * SLIDER_SCALE));
                a21.setValue((int) (iHatInit.getVectorY() * SLIDER_SCALE));
                a22.setValue((int) (jHatInit.getVectorY() * SLIDER_SCALE));
                fireTransformEvent(new TransformEvent(this, a11.getValue(), a12.getValue(), a21.getValue(), a22.getValue()));
            }
        });

        JButton clear = new JButton("Clear vectors");
        clear.addActionListener(e -> gridRef.clearVectors());

        JButton quit = new JButton("Quit");
        quit.addActionListener(e -> {
            exploreRef.fireExitEvent();
            gridRef.clearVectors();
        });

        quit.setFont(font);
        clear.setFont(font);
        identity.setFont(font);
        transform.setFont(font);

        matrixDisplay = new MatrixDisplay(iHatInit.getVectorX(), jHatInit.getVectorX(), iHatInit.getVectorY(), jHatInit.getVectorY(), font);
        matrixDisplay.setBorders(size.width / 4);
        gc.weighty = 0.0;
        gc.insets = new Insets(1, 0, 1, 0);
        gc.fill = GridBagConstraints.BOTH;

        gc.anchor = GridBagConstraints.CENTER;
        gc.gridx = 0;
        gc.gridy = 0;
        gb.setConstraints(a11, gc);
        add(a11);

        gc.gridx = 1;
        gc.gridy = 0;
        gb.setConstraints(a12, gc);
        add(a12);

        gc.gridx = 0;
        gc.gridy = 1;
        gb.setConstraints(a21, gc);
        add(a21);

        gc.gridx = 1;
        gc.gridy = 1;
        gb.setConstraints(a22, gc);
        add(a22);

        gc.insets = new Insets(0, 0, 15, 0);
        gc.fill = GridBagConstraints.BOTH;
        gc.gridwidth = 2;
        gc.gridx = 0;
        gc.gridy = 2;
        gb.setConstraints(matrixDisplay, gc);
        add(matrixDisplay);

        gc.gridx = 0;
        gc.gridy = 3;
        gc.gridwidth = 2;
        gb.setConstraints(transform, gc);
        add(transform);

        gc.gridx = 0;
        gc.gridy = 4;
        gc.gridwidth = 2;
        gb.setConstraints(identity, gc);
        add(identity);

        if (special) {
            gc.gridx = 0;
            gc.gridy = 5;
            gc.gridwidth = 2;
            gb.setConstraints(clear, gc);
            add(clear);

            gc.gridx = 0;
            gc.gridy = 6;
            gc.gridwidth = 2;
            gb.setConstraints(quit, gc);
            add(quit);
        }
    }

    private JSlider addSlider(int startValue) {
        JSlider jSlider = new JSlider(-SLIDER_OPTIONS, SLIDER_OPTIONS, startValue);
        jSlider.addChangeListener(e -> matrixDisplay.updateMatrix(
                ((double) a11.getValue()) / SLIDER_SCALE,
                ((double) a12.getValue()) / SLIDER_SCALE,
                ((double) a21.getValue()) / SLIDER_SCALE,
                ((double) a22.getValue()) / SLIDER_SCALE));
        Dimension size = jSlider.getPreferredSize();
        size.width = getPreferredSize().width / 2;
        size.height = 25;
        jSlider.setMinimumSize(size);
        return jSlider;
    }

    public void setGridRef(LinalgGrid gridRef) {
        this.gridRef = gridRef;
    }

    public void setExploreRef(Explore exploreRef) {
        this.exploreRef = exploreRef;
    }

    private void fireTransformEvent(TransformEvent e) {
        Object[] listeners = listenerList.getListenerList(); // get all listeners

        for (int i = 0; i < listeners.length; i += 2) // step by 2 at a time because listenerList is like classType1, listener1, classType2, listener2, classType3, listener3,
        { // thus all the even numbered indices are just the classes, and the odd numbered ones are the actual listeners
            if (listeners[i] == TransformEventListener.class) { // if the listener happens to be a ColorPanelListener, we can now fire colorChanged (equivalent to "actionPerformed")
                ((TransformEventListener) listeners[i + 1]).applyTransform(e);
            }
        }
    }

    public void addTransformListener(TransformEventListener listener) {
        listenerList.add(TransformEventListener.class, listener);
    }
}

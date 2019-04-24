//---------------------------------------------------------------------------------------|
//  LinalgGrid.java - Grid for drawing vectors and demonstrating linear transformations, |
//                    used in every mode.                                                |
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
//  Input: Lotsa stuff, including mouse positions to add new vectors, way too many to list|
//  Output: Visual representation of the vectors on a grid that allows you to apply linear|
//          transformations                                                              |
//---------------------------------------------------------------------------------------|
package MathBase;

import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionListener;
import java.util.ArrayList;

public class LinalgGrid extends JPanel {
    private static final int halfLinesNum = 100, majorGridWidth = 2, axisWidth = 3, minorGridWidth = 1;
    private static final Color majorGridColor = Color.cyan,
            minorGridColor = Color.darkGray,
            axisColor = Color.white;
    static int ORIGIN_X, ORIGIN_Y;
    private static Vector2D iHatFixed, jHatFixed;
    private static int left, top, wideness, tallness;
    VectorList arrowList;
    private VectorList dragList;
    private Vector2D iHat, jHat;
    private Vector2D selected;
    private boolean drawBasis;
    private int addAllowed;

    public LinalgGrid() {
        this(true, true);
    }      // if nothing, then drawBasis and there is a left Panel

    public LinalgGrid(boolean leftPanel) {
        this(leftPanel, true);
    }  // if one boolean it refers to leftPanel being there or not

    public LinalgGrid(boolean leftPanel, boolean drawBasis) {
        this(null, null, drawBasis, leftPanel, true, 9999);
    }

    public LinalgGrid(boolean leftPanel, boolean drawBasis, boolean rightPanel) {
        this(null, null, drawBasis, leftPanel, rightPanel, 9999);
    }

    public LinalgGrid(Vector2D iHat, Vector2D jHat, boolean drawBasis, boolean leftPanel, boolean rightPanel, int addAllowedIn) {
        this.drawBasis = drawBasis;

        if (iHat != null)
            this.iHat = new Vector2D(iHat);
        else
            this.iHat = new Vector2D(1, 0);

        if (jHat != null)
            this.jHat = new Vector2D(jHat);

        else
            this.jHat = new Vector2D(0, 1);

        iHatFixed = new Vector2D(1, 0, Color.green);
        jHatFixed = new Vector2D(0, 1, Color.red);

        if (leftPanel && rightPanel) {   // if right and left panels
            ORIGIN_X = 560;
            ORIGIN_Y = 500;
        } else if (leftPanel) {        // if left panel only
            ORIGIN_X = 740;
            ORIGIN_Y = 500;
        } else if (rightPanel) {       // if right panel only
            ORIGIN_X = 800;
            ORIGIN_Y = 500;
        } else {                       // if no panels at all (explore mode)
            ORIGIN_X = 1000;
            ORIGIN_Y = 500;
        }


        left = 0;
        top = 0;
        wideness = getWidth();
        tallness = getHeight();
        arrowList = new VectorList(this);
        dragList = new VectorList(this);

        this.addAllowed = addAllowedIn;

        addMouseListener(new MouseListener() {
            @Override
            public void mouseClicked(MouseEvent e) {  // pressed and released
                if (SwingUtilities.isRightMouseButton(e)) {
                    if (dragList.length() < addAllowed) {
                        Point pos = e.getPoint();
                        addDraggable(new Vector2D(pos, iHatGet(), jHatGet()));
                    }
                }
            }

            @Override
            public void mousePressed(MouseEvent e) {
                Point pos = e.getPoint();
                selected = trySelect(pos.x, pos.y);
            }

            @Override
            public void mouseReleased(MouseEvent e) {
                selected = null;

            }

            @Override
            public void mouseEntered(MouseEvent e) {

            }

            @Override
            public void mouseExited(MouseEvent e) {

            }
        });

        addMouseMotionListener(new MouseMotionListener() {
            @Override
            public void mouseDragged(MouseEvent e) {
                if (selected != null) {
                    Point pos = e.getPoint();
                    selected.setScreenPos(pos.x, pos.y, iHatGet(), jHatGet());
                    repaint();
                }
            }

            @Override
            public void mouseMoved(MouseEvent e) {

            }
        });
    }


    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setBackground(Color.black);    // draw background
        g2.fillRect(left, top, wideness + 20000, tallness + 20000);

        g2.setStroke(new BasicStroke(minorGridWidth));
        drawBasisGrid(g2, iHatFixed, jHatFixed, minorGridColor);

        g2.setStroke(new BasicStroke(majorGridWidth));
        drawBasisGrid(g2, iHat, jHat, majorGridColor);

        g2.setStroke(new BasicStroke(axisWidth));
        iHatFixed.drawRay(g2, axisColor);
        jHatFixed.drawRay(g2, axisColor);

        if (drawBasis) {
            g2.setStroke(new BasicStroke(axisWidth));
            jHatFixed.drawArrow(g2, iHat, jHat);
            iHatFixed.drawArrow(g2, iHat, jHat);
        }

        arrowList.paintComponent(g);
        dragList.paintComponent(g);
    }


    private void drawBasisGrid(Graphics2D g2, Vector2D basisOne, Vector2D basisTwo, Color color) {
        for (int i = -halfLinesNum; i <= halfLinesNum; i++) {
            for (int j = -halfLinesNum; j <= halfLinesNum; j++) {
                if (i != 0 || j != 0) {
                    Vector2D drawHorizontal = basisOne.scale(i);
                    Vector2D drawVertical = basisTwo.scale(j);
                    drawHorizontal.drawRay(g2, drawVertical, color);
                    drawVertical.drawRay(g2, drawHorizontal, color);
                }
            }
        }
    }

    void changeBasis(Vector2D iHatNew, Vector2D jHatNew) {
        iHat = iHatNew;
        jHat = jHatNew;
        repaint();
    }

    public ArrayList<Vector2D> getDraggable() {
        return dragList.getVectors();
    }


    private void addDraggable(Vector2D drag) {
        dragList.addVector(drag);
        repaint();
    }

    public void addVector(Vector2D vector) {
        arrowList.addVector(vector);
        repaint();
    }

    public void scaleAnimate(ScaleAnimatorTimer sat) {   // sets off the animation, calling .start() on the timer
        arrowList.scaleAnimate(sat);
    }

    public void translateAnimate(TranslateAnimatorTimer tat) {
        arrowList.translateAnimate(tat);
    }


    void scaleByID(int ID, Vector2D newVal) {
        arrowList.scaleVectorByID(ID, newVal);  // actually does the steps of the animation
    }

    void translateByID(int ID, Vector2D newOffset) {
        arrowList.translateVectorByID(ID, newOffset);
    }

    void setTranslateByID(int ID, Vector2D newOffset) {
        arrowList.getArrowByID(ID).setOffset(newOffset);
    }

    public void clearVectors() {
        arrowList.clear();
        dragList.clear();
        repaint();
        revalidate();
    }

    public void removeByID(int ID) {
        arrowList.removeByID(ID);
        repaint();
        revalidate();
    }


    public void addEigen(Vector2D iHatNew, Vector2D jHatNew){
        // compute coefficients a,b,c for solving ax^2 + bx + c = 0
        removeByID(-1);
        removeByID(-2);
        double a = 1.0;
        double b = -(jHatNew.getVectorY()+iHatNew.getVectorX());
        double c = (iHatNew.getVectorX()*jHatNew.getVectorY()) - (iHatNew.getVectorY()*jHatNew.getVectorX());
        double discrim = b*b-4*a*c;
        if (discrim >= 0) {
            double sqrtDiscrim = Math.sqrt(discrim);
            double eig1 = (-b+sqrtDiscrim)/(2*a);
            double eig2 = (-b-sqrtDiscrim)/(2*a);
            Vector2D eigVec1, eigVec2;
            if (jHatNew.getVectorX() != 0) {
                eigVec1 = (new Vector2D(1.0, (eig1 - iHatNew.getVectorX()) / jHatNew.getVectorX())).norm();
                eigVec2 = (new Vector2D(1.0, (eig2 - iHatNew.getVectorX()) / jHatNew.getVectorX())).norm();
            }
            else if (iHatNew.getVectorY() != 0){
                eigVec1 = (new Vector2D((eig1 - jHatNew.getVectorY()) / iHatNew.getVectorY(), 1)).norm();
                eigVec2 = (new Vector2D((eig2 - jHatNew.getVectorY()) / iHatNew.getVectorY(), 1)).norm();
            }
            else if ((eig1 - iHatNew.getVectorX() != 0) && (eig2 - iHatNew.getVectorX() != 0)){
                eigVec1 = (new Vector2D((jHatNew.getVectorY()) / (eig1 - iHatNew.getVectorX()), 1)).norm();
                eigVec2 = (new Vector2D((jHatNew.getVectorY()) / (eig2 - iHatNew.getVectorX()), 1)).norm();
            }
            else if ((eig1 - jHatNew.getVectorY() != 0) && (eig2 - jHatNew.getVectorY() != 0)) {
                eigVec1 = (new Vector2D(1, (iHatNew.getVectorY()) / (eig1 - jHatNew.getVectorY()))).norm();
                eigVec2 = (new Vector2D(1, (iHatNew.getVectorY()) / (eig2 - jHatNew.getVectorY()))).norm();
            }
            else {
                eigVec1 = new Vector2D(0, 0, "-1");
                eigVec2 = new Vector2D(0, 0, "-2");
            }
            addVector(eigVec1);
            addVector(eigVec2);
            System.out.println("Computed eigenvalues of [value=" + eig1 + ", vector=" + eigVec1 + "] and [value=" + eig2 + ", vector=" + eigVec2 + "]");
        }
        else {
            System.out.println("Eigenvalues could not be found (-ve discriminant => singular matrix)");
        }
    }


    public Vector2D iHatGet() {
        return iHat;
    }

    public Vector2D jHatGet() {
        return jHat;
    }

    private Vector2D trySelect(double mouseX, double mouseY) {
        return dragList.trySelect(mouseX, mouseY);
    }

    public void retransform(Vector2D iHatDesired, Vector2D jHatDesired) {
        GridAnimatorThread gridAnimate;
        if (iHatDesired == null && jHatDesired != null)  // handling if one or the other basis vectors is null
            gridAnimate = new GridAnimatorThread(this, iHat, jHatDesired);
        else if (iHatDesired != null && jHatDesired == null)
            gridAnimate = new GridAnimatorThread(this, iHatDesired, jHat);
        else if (iHatDesired != null && jHatDesired != null)
            gridAnimate = new GridAnimatorThread(this, iHatDesired, jHatDesired);
        else
            gridAnimate = new GridAnimatorThread(this, iHat, jHat);

        gridAnimate.start();
    }

    public void setAddAllowed(int addAllowed) {
        this.addAllowed = addAllowed;
        repaint();
        revalidate();
    }

    public void setDrawBasis(boolean drawBasis) {
        this.drawBasis = drawBasis;
        repaint();
        revalidate();
    }
}

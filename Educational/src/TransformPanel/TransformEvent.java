package TransformPanel;

import MathBase.Vector2D;

import java.util.EventObject;


public class TransformEvent extends EventObject {
    private double a11, a12, a21, a22;

    public TransformEvent(Object source, double a11, double a12, double a21, double a22) {
        super(source);
        this.a11 = a11;
        this.a12 = a12;
        this.a21 = a21;
        this.a22 = a22;
    }

    public Vector2D iHatGet() {
        return new Vector2D(a11 / TransformPanel.SLIDER_SCALE, a21 / TransformPanel.SLIDER_SCALE);
    }

    public Vector2D jHatGet() {
        return new Vector2D(a12 / TransformPanel.SLIDER_SCALE, a22 / TransformPanel.SLIDER_SCALE);
    }
}

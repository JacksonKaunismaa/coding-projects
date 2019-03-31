//---------------------------------------------------------------------------------------|
//  GridAnimatorThread.java - Animator thread for applying a linear transformation to the|
//                            grid, by repeatedly changing the basis for it, so it can   |
//                            asynchronously be displayed while the user does other stuff|
//---------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                            |
//  Date: 2019-01-15                                                                     |
//---------------------------------------------------------------------------------------|
//  Input: 2 new Vector2Ds that are to be the new basis (for linear transformations)     |
//  Output: Visual representation of the linear transformation slowly being applied by   |
//          moving the basis vectors to the desired position and redrawing the grid      |
//---------------------------------------------------------------------------------------|
package MathBase;

public class GridAnimatorThread extends Thread {

    private double animateAmount;        // percentage of the animation completed (goes from 0->1)
    private Vector2D iHatStart, jHatStart; // Copies of initial iHat and jHat
    private Vector2D iHatEnd, jHatEnd;    // desired final location for the basis vectors
    private LinalgGrid grid;              // reference to the grid so we can repeatedly draw the grid and update its basis

    // constructor method
    GridAnimatorThread(LinalgGrid grid, Vector2D iHatEnd, Vector2D jHatEnd) {
        animateAmount = 0.0;
        this.grid = grid;
        this.iHatStart = grid.iHatGet();
        this.jHatStart = grid.jHatGet();
        this.iHatEnd = iHatEnd;
        this.jHatEnd = jHatEnd;
    }

    public void run() {
        while (animateAmount <= 1.0001) {
            Vector2D iHatNew = iHatEnd.scale(animateAmount).add(iHatStart.scale(1 - animateAmount));
            Vector2D jHatNew = jHatEnd.scale(animateAmount).add(jHatStart.scale(1 - animateAmount));
            grid.changeBasis(iHatNew, jHatNew);
            animateAmount += 0.02;
            try {
                Thread.sleep(25);
            } catch (InterruptedException ignored) {
            }
        }
        grid.changeBasis(iHatEnd, jHatEnd);
    }
}

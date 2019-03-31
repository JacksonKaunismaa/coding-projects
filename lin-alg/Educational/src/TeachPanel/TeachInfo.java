//----------------------------------------------------------------------------------------|
//  TeachInfo.java - Parsing and reading questions that TeachPanel.java interprets as     |
//  questions to test the user on, understands the markup language using regex.           |
//----------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                             |
//  Date: 2019-01-15                                                                      |
//----------------------------------------------------------------------------------------|
//  Input: File text formatted like a markup language                                     |
//  Output: Question that the user can be asked, and vectors/animations for the grid      |
//----------------------------------------------------------------------------------------|
package TeachPanel;

import MathBase.ScaleAnimatorTimer;
import MathBase.TranslateAnimatorTimer;
import MathBase.Vector2D;

import java.awt.*;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class TeachInfo {
    protected String lineInfo;
    protected ArrayList<Vector2D> foundVector;
    private Matcher textMatcher, vectorMatcher, basisMatcher, transformMatcher, basisVisibleMatcher, addingAllowedMatcher, animateMatcher, removeMatcher;
    private String foundText;
    private ArrayList<TranslateAnimatorTimer> foundTranslations;
    private ArrayList<ScaleAnimatorTimer> foundScalings;
    private ArrayList<Integer> foundRemove;
    private Vector2D[] foundBasisChange;
    private boolean foundIsTransform, foundBasisVisible;
    private int foundAddingAllowed;

    public TeachInfo(String lineInfo) {
        this.lineInfo = lineInfo;
        textMatcher = Pattern.compile("<text>(.+?)</text>").matcher(lineInfo);
        vectorMatcher = Pattern.compile("<vector>(.+?)</vector>").matcher(lineInfo);
        basisMatcher = Pattern.compile("<([ij])hat>(.+?),(.+?)</\\1hat>").matcher(lineInfo);
        transformMatcher = Pattern.compile("<transform=(.)>").matcher(lineInfo);
        basisVisibleMatcher = Pattern.compile("<visible=(.)>").matcher(lineInfo);
        addingAllowedMatcher = Pattern.compile("<add=(\\d+)>").matcher(lineInfo);
        animateMatcher = Pattern.compile("<animate>(.+?)</animate>").matcher(lineInfo);
        removeMatcher = Pattern.compile("<remove>(.+?)</remove>").matcher(lineInfo);

        foundText = null;
        foundVector = null;
        foundBasisChange = null;
        foundTranslations = null;
        foundScalings = null;
        foundRemove = null;

        foundIsTransform = false;
        foundBasisVisible = false;
        foundAddingAllowed = -1;
    }

    public String findDisplayInfo() {
        if (foundText == null) {
            if (textMatcher.find()) {
                foundText = textMatcher.group(1);
            } else {
                System.out.println("No text found!");
                return "-=-=-=-=-=-=";
            }
        }
        return "<html>" + foundText + "</html>";
    }

    public boolean isTransformPanel() {
        if (!foundIsTransform) {  // if its false, check if it should be true
            if (transformMatcher.find()) {   // check if there is a match (only works once)
                foundIsTransform = transformMatcher.group(1).equals("t");     // all subsequent calls now evaluate to whatever the correct answer should be (true or false)
            }
        }
        return foundIsTransform;
    }

    public boolean basisVisible() {
        if (!foundBasisVisible) {  // if its false, check if it should be true
            if (basisVisibleMatcher.find()) {   // check if there is a match (only works once)
                foundBasisVisible = basisVisibleMatcher.group(1).equals("t");     // all subsequent calls now evaluate to whatever the correct answer should be (true or false)
            }
        }
        return foundBasisVisible;
    }

    public int addingAllowed() {
        if (foundAddingAllowed == -1) {  // if its false, check if it should be true
            foundAddingAllowed = 0;
            if (addingAllowedMatcher.find()) {   // check if there is a match (only works once)
                foundAddingAllowed = Integer.parseInt(addingAllowedMatcher.group(1));     // all subsequent calls now evaluate to whatever the correct answer should be (true or false)
            }
        }
        return foundAddingAllowed;
    }

    protected Color colorMap(String letter) {
        switch (letter) {
            case "G":
                return Color.green;
            case "B":
                return Color.blue;
            case "Y":
                return Color.yellow;
            case "O":
                return new Color(251, 102, 0);
            case "R":
                return Color.red;
            case "P":
                return Color.lightGray; //  Pale
            case "W":
                return Color.white;
            default:
                return Color.gray;
        }
    }

    public Vector2D[] findBasisChange() {
        if (foundBasisChange == null) {
            Vector2D iHatNew = null;
            Vector2D jHatNew = null;
            while (basisMatcher.find()) {
                if (basisMatcher.group(1).equals("i"))
                    iHatNew = new Vector2D(Double.parseDouble(basisMatcher.group(2)), Double.parseDouble(basisMatcher.group(3)));
                if (basisMatcher.group(1).equals("j"))
                    jHatNew = new Vector2D(Double.parseDouble(basisMatcher.group(2)), Double.parseDouble(basisMatcher.group(3)));
            }
            foundBasisChange = new Vector2D[]{iHatNew, jHatNew};
        }
        return foundBasisChange;
    }

    public ArrayList<Vector2D> getVectorInfo() {
        if (foundVector == null) {
            foundVector = new ArrayList<>();
            if (vectorMatcher.find()) {
                String vectorStrings = vectorMatcher.group(1);
                findVectorInfo(vectorStrings);
            }
        }
        return foundVector;
    }

    protected void findVectorInfo(String vectorStrings) {
        Matcher vectorGetter = Pattern.compile("\\((.+?),(.+?),(.),?(.*?)\\+?(\\((.+?),(.+?),(\\d+))?\\)").matcher(vectorStrings);
        while (vectorGetter.find()) {
            Vector2D addVec = new Vector2D(
                    Double.parseDouble(vectorGetter.group(1)),
                    Double.parseDouble(vectorGetter.group(2)),
                    colorMap(vectorGetter.group(3)),
                    vectorGetter.group(4));

            if (vectorGetter.group(6) != null) {
                Vector2D offsetVec = new Vector2D(
                        Double.parseDouble(vectorGetter.group(6)),
                        Double.parseDouble(vectorGetter.group(7)),
                        vectorGetter.group(8));
                addVec.setOffset(offsetVec);
            }
            foundVector.add(addVec);
        }
    }

    public void clearVectors() {
        foundVector = null;
    }

    public void clearAnimations() {
        if (foundScalings != null)
            foundScalings.clear();
        if (foundTranslations != null)
            foundTranslations.clear();
    }

    public ArrayList<Integer> getRemove() {
        if (foundRemove == null) {
            foundRemove = new ArrayList<>();
            if (removeMatcher.find()) {
                String removeString = removeMatcher.group(1);
                Matcher removeGetter = Pattern.compile("([^,;=()]+)").matcher(removeString);
                while (removeGetter.find()) {
                    foundRemove.add(Integer.parseInt(removeGetter.group(1)));
                }
            }
        }
        return foundRemove;
    }

    private void parseTranslations(String animateString, TeachPanel teachPanel) {
        if (foundTranslations == null)
            foundTranslations = new ArrayList<>();
        Matcher translateGetter = Pattern.compile("\\((\\d+)\\.trans\\((.+?),(.+?)\\)\\)").matcher(animateString);
        while (translateGetter.find()) {
            foundTranslations.add(new TranslateAnimatorTimer(
                    Integer.parseInt(translateGetter.group(1)),
                    new Vector2D(Double.parseDouble(translateGetter.group(2)),
                            Double.parseDouble(translateGetter.group(3))),
                    teachPanel));
        }
    }

    public ArrayList<ScaleAnimatorTimer> getScaling(TeachPanel teachPanel) {
        if (foundScalings == null)
            foundScalings = new ArrayList<>();
        if (animateMatcher.find()) {
            String animateString = animateMatcher.group(1);
            parseTranslations(animateString, teachPanel);
            Matcher animateGetter = Pattern.compile("\\((\\d+)\\.scale\\((.+?)\\)\\)").matcher(animateString);
            while (animateGetter.find()) {
                foundScalings.add(new ScaleAnimatorTimer(
                        Integer.parseInt(animateGetter.group(1)),
                        Double.parseDouble(animateGetter.group(2)),
                        teachPanel));
            }
        }
        return foundScalings;
    }

    public ArrayList<TranslateAnimatorTimer> getTranslations() {
        if (foundTranslations != null)
            return foundTranslations;
        else
            return new ArrayList<>();
    }
}

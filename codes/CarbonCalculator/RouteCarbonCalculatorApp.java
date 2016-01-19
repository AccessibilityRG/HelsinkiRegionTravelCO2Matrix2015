package routecarboncalculatorapp;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Scanner;

/**
 *
 * @author 
 */
public class RouteCarbonCalculatorApp {

    private static final String NAME_AND_VERSION = "RouteCarbonCalculator 1.3, 2015-01-30";

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws IOException {
        long alkuaika = System.currentTimeMillis();

        long ohitettuVirheina = 0;
        long korjattuVirheita = 0;
        int fileType = 1; //1=normaalifile, 2=virhefile

        int rowCounter = 0;

        HashMap<String, Integer> tunnistusTaulukko = new HashMap<String, Integer>();

        String sRow;

        if (args.length == 0) {
            System.out.println();
            System.out.println(NAME_AND_VERSION);
            System.out.println("Käyttö: java -jar RouteCarbonCalculator.jar <syöttötiedoston nimi>");
            System.out.println();
            System.exit(-1);
        }

        String input_file = args[0];
        System.out.println("Input-tiedosto on " + input_file);
        File inFile = new File(input_file);

        String inputWithoutExtension = input_file.substring(0, input_file.length() - 4);

        String output_file = args[1];
        System.out.println("Output-tiedosto on " + output_file);

        //String error_file = inputWithoutExtension + ".ERRORS.csv";
        String error_file = args[2];
        System.out.println("Error-tiedosto on " + error_file);

        PrintWriter outFile = new PrintWriter(new FileWriter(output_file));
        PrintWriter errFile = new PrintWriter(new FileWriter(error_file));

        PrintWriter ttFile = new PrintWriter(new FileWriter("ttFile.txt"));

        System.out.println("Luodaan tunnistustaulukko.");
        tunnistusTaulukko = createRouteHash(inFile);

        ttFile.close();

        Scanner s = new Scanner(new BufferedReader(new FileReader(inFile)));

        System.out.println("Aloitetaan input-tiedoston luku.");

        outFile.print("RouteID;");
        outFile.print("from_id;");
        outFile.print("to_id;");
        outFile.print("Walk;");
        outFile.print("Bus;");
        outFile.print("Bus CO2;");
        outFile.print("Tram;");
        outFile.print("Tram CO2;");
        outFile.print("Train;");
        outFile.print("Train CO2;");
        outFile.print("Metro;");
        outFile.print("Metro CO2;");
        outFile.print("Ferry;");
        outFile.print("Ferry CO2;");
        outFile.print("Lines used;");
        outFile.print("Total CO2;");
        outFile.print("CO2 comparison (car)");
        outFile.println();

        try {
            s.useDelimiter("\r\n|\n|\r");
            s.nextLine();
            while (s.hasNext()) {
                rowCounter++;
                RouteCarbonCalculator rd = new RouteCarbonCalculator();
                sRow = s.nextLine();

                String modRow = sRow.replace('#', ';');

		//System.out.println("modRow: " + modRow);
                try {
                    if (rd.processRow(modRow, tunnistusTaulukko)) {
                        rd.printDistancesToFile(outFile);
                    } else {
                        errFile.println(rowCounter + ":" + sRow);
                        ohitettuVirheina++;
                        continue;
                    }
                } catch (IOException e) {
                    errFile.println(rowCounter + ";" + sRow);
                    ohitettuVirheina++;
                    continue;
                }

                rd = null;
            }
        } finally {
            if (s != null) {
                s.close();
            }
        }

        System.out.println("Virheellisiä rivejä: " + ohitettuVirheina);
        outFile.close();
        long loppuaika = System.currentTimeMillis();

        System.out.println("Käsittely kesti " + (loppuaika - alkuaika) + " ms");

    }

    private static HashMap<String, Integer> createRouteHash(File inFile) throws FileNotFoundException {
        HashMap<String, Integer> hm = new HashMap<String, Integer>();
        Scanner s = new Scanner(new BufferedReader(new FileReader(inFile)));

        String sRow;
        Integer transportType = 0;
        String lineString = "";

        try {
            s.useDelimiter("\r\n|\n|\r");
            s.nextLine();
            while (s.hasNext()) {
                sRow = s.nextLine();

                String modRow = sRow.replace('#', ';');

                Scanner ss = new Scanner(modRow);
                ArrayList<String> splitRow = new ArrayList<String>();

                ss.useDelimiter(";");

                while (ss.hasNext()) {
                    splitRow.add(ss.next());
                }
                ss.close();

                for (int i = 0; i < splitRow.size() - 1; i++) {
                    if (splitRow.get(i).equals("LINE")) {
                        try {
                            //vanha: lineString    = splitRow.get(i+1).toString();
                            lineString = splitRow.get(i + 4).toString();
                            //System.out.println("lineString: " + lineString);

                            //vanha: transportType = Integer.valueOf(splitRow.get(i+2));
                            transportType = Integer.valueOf(splitRow.get(i + 5));
                            //System.out.println("transportType: " + transportType);
                        } catch (NumberFormatException nfe) {
                            continue;
                        }
                        if (lineString.compareTo("") > 0 && transportType != 0) {
                            hm.put(lineString, transportType);
                        }
                    }
                }
            }
        } finally {
            s.close();
        }

        return hm;
    }

}

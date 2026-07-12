import java.sql.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.io.*;
import java.time.*;
import java.time.format.*;

public class RdpLoadTest {

    static String WAREHOUSE;
    static String TABLE;
    static String JDBC_URL;
    static String PRIVATE_KEY_PATH;
    static String USER;
    static int NUM_CONNECTIONS;
    static int DURATION_SECONDS;
    static int RAMP_UP_SECONDS;
    static String QUERY_MIX;
    static String EXEC_MODE;
    static String TICKER_BIAS;
    static int RESULT_LIMIT;
    static long[] TS_HASH_POOL;
    static long[] HOT_TICKER_POOL;
    static String[] TS_CD_POOL;
    static String SESSION_V1_QUERY_API = "unknown";
    static String SESSION_PREFETCH_THREADS = "unknown";

    public static void main(String[] args) throws Exception {
        WAREHOUSE = getArg(args, "--warehouse", "RDP_STANDARD_WH");
        TABLE = getArg(args, "--table", "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION");
        USER = getArg(args, "--user", "JACK");
        PRIVATE_KEY_PATH = getArg(args, "--key", "keys/rsa_key.p8");
        NUM_CONNECTIONS = Integer.parseInt(getArg(args, "--connections", "10"));
        DURATION_SECONDS = Integer.parseInt(getArg(args, "--duration", "30"));
        RAMP_UP_SECONDS = Integer.parseInt(getArg(args, "--rampup", "30"));
        QUERY_MIX = getArg(args, "--mix", "mixed");
        EXEC_MODE = getArg(args, "--mode", "sync");
        TICKER_BIAS = getArg(args, "--ticker_bias", "uniform");
        RESULT_LIMIT = Integer.parseInt(getArg(args, "--result_limit", "0"));

        String account = getArg(args, "--account", "SFSEEUROPE-EU_DEMO59");
        String db = getArg(args, "--database", "THEMES_RESEARCH_DEMO");
        String schema = getArg(args, "--schema", "RAW_DATA");
        JDBC_URL = "jdbc:snowflake://" + account + ".snowflakecomputing.com/?db=" + db + "&schema=" + schema + "&warehouse=" + WAREHOUSE;

        if (QUERY_MIX.startsWith("tscd")) {
            TS_CD_POOL = loadTsCdPool();
            TS_HASH_POOL = new long[0];
            HOT_TICKER_POOL = new long[0];
            System.err.println("Loaded " + TS_CD_POOL.length + " TS_CD values");
        } else {
            TS_HASH_POOL = loadTickerPool();
            HOT_TICKER_POOL = new long[Math.min(1000, TS_HASH_POOL.length)];
            System.arraycopy(TS_HASH_POOL, 0, HOT_TICKER_POOL, 0, HOT_TICKER_POOL.length);
            System.err.println("Loaded " + TS_HASH_POOL.length + " tickers (hot pool: " + HOT_TICKER_POOL.length + ")");
        }

        captureSessionParams();

        System.err.println("Starting load test: " + NUM_CONNECTIONS + " connections x " + DURATION_SECONDS + "s");

        runLoadTest();
    }

    static Properties getConnectionProps() {
        Properties props = new Properties();
        props.put("user", USER);
        props.put("private_key_file", PRIVATE_KEY_PATH);
        props.put("warehouse", WAREHOUSE);
        props.put("CLIENT_SESSION_KEEP_ALIVE", "true");
        props.put("CLIENT_RESULT_CHUNK_SIZE", "16");
        props.put("CLIENT_RESULT_PREFETCH_THREADS", "8");
        props.put("APPLICATION", "RDP_TEST_HARNESS_JAVA");
        props.put("tracing", "OFF");
        return props;
    }

    static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(JDBC_URL, getConnectionProps());
    }

    static void captureSessionParams() {
        try {
            Connection conn = getConnection();
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SHOW PARAMETERS LIKE 'CLIENT_PREFETCH_THREADS' IN SESSION");
            while (rs.next()) {
                SESSION_PREFETCH_THREADS = rs.getString("value");
            }
            rs.close();
            rs = stmt.executeQuery("SHOW PARAMETERS LIKE 'CLIENT_USE_V1_QUERY_API' IN SESSION");
            while (rs.next()) {
                SESSION_V1_QUERY_API = rs.getString("value");
            }
            rs.close();
            if (SESSION_V1_QUERY_API.equals("unknown")) {
                SESSION_V1_QUERY_API = "check_jdbc_logs";
            }
            stmt.close();
            conn.close();
            System.err.println("Session params: CLIENT_USE_V1_QUERY_API=" + SESSION_V1_QUERY_API + ", PREFETCH_THREADS=" + SESSION_PREFETCH_THREADS);
        } catch (Exception e) {
            System.err.println("Failed to capture session params: " + e.getMessage());
        }
    }

    static long[] loadTickerPool() throws Exception {
        Connection conn = getConnection();
        Statement stmt = conn.createStatement();
        String poolWh = isInteractiveTable() ? "RDP_STANDARD_WH" : WAREHOUSE;
        stmt.execute("USE WAREHOUSE " + poolWh);
        String poolTable = isInteractiveTable() ? "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION" : TABLE;
        ResultSet rs = stmt.executeQuery("SELECT DISTINCT TS_HASH FROM " + poolTable + " SAMPLE (1000000 ROWS)");
        List<Long> hashes = new ArrayList<>();
        while (rs.next()) {
            hashes.add(rs.getLong(1));
        }
        rs.close();
        stmt.close();
        conn.close();
        return hashes.stream().mapToLong(Long::longValue).toArray();
    }

    static long pickTicker(Random rng) {
        if ("hot80".equals(TICKER_BIAS) && rng.nextDouble() < 0.8) {
            return HOT_TICKER_POOL[rng.nextInt(HOT_TICKER_POOL.length)];
        }
        if ("hot50".equals(TICKER_BIAS) && rng.nextDouble() < 0.5) {
            return HOT_TICKER_POOL[rng.nextInt(HOT_TICKER_POOL.length)];
        }
        return TS_HASH_POOL[rng.nextInt(TS_HASH_POOL.length)];
    }

    static String[] loadTsCdPool() throws Exception {
        Connection conn = getConnection();
        Statement stmt = conn.createStatement();
        String poolWh = isInteractiveTable() ? "RDP_STANDARD_WH" : WAREHOUSE;
        stmt.execute("USE WAREHOUSE " + poolWh);
        ResultSet rs = stmt.executeQuery("SELECT DISTINCT TS_CD FROM " + TABLE + " SAMPLE (1000000 ROWS)");
        List<String> cds = new ArrayList<>();
        while (rs.next()) {
            cds.add(rs.getString(1));
        }
        rs.close();
        stmt.close();
        conn.close();
        return cds.toArray(new String[0]);
    }

    static String pickTsCd(Random rng) {
        return TS_CD_POOL[rng.nextInt(TS_CD_POOL.length)];
    }

    static String generateTsCdSingleQuery(Random rng) {
        String tsCd = pickTsCd(rng);
        return applyLimit("SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM " + TABLE +
               " WHERE TS_CD = '" + tsCd.replace("'", "''") + "'" +
               " ORDER BY DATE_VALUE DESC");
    }

    static String generateTsCdDateRangeQuery(Random rng) {
        String tsCd = pickTsCd(rng);
        int startYear = 2020 + rng.nextInt(4);
        int startMonth = 1 + rng.nextInt(12);
        String startDate = String.format("%d-%02d-01", startYear, startMonth);
        int rangeMonths = 6 + rng.nextInt(24);
        int endYear = startYear + (startMonth + rangeMonths - 1) / 12;
        int endMonth = (startMonth + rangeMonths - 1) % 12 + 1;
        String endDate = String.format("%d-%02d-28", endYear, endMonth);
        return applyLimit("SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM " + TABLE +
               " WHERE TS_CD = '" + tsCd.replace("'", "''") + "'" +
               " AND DATE_VALUE BETWEEN '" + startDate + "' AND '" + endDate + "'" +
               " ORDER BY DATE_VALUE DESC");
    }

    static String generateTsCdMultiQuery(Random rng) {
        int numTickers = 5 + rng.nextInt(6);
        Set<String> cds = new HashSet<>();
        while (cds.size() < numTickers) {
            cds.add(pickTsCd(rng));
        }
        StringBuilder sb = new StringBuilder();
        sb.append("SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM ").append(TABLE);
        sb.append(" WHERE TS_CD IN (");
        boolean first = true;
        for (String cd : cds) {
            if (!first) sb.append(",");
            sb.append("'").append(cd.replace("'", "''")).append("'");
            first = false;
        }
        sb.append(") ORDER BY TS_CD, DATE_VALUE DESC");
        return applyLimit(sb.toString());
    }

    static String generateMultiTickerQuery(Random rng) {
        int numTickers = 8 + rng.nextInt(Math.min(13, TS_HASH_POOL.length - 8 + 1));
        Set<Long> hashes = new HashSet<>();
        while (hashes.size() < numTickers) {
            hashes.add(pickTicker(rng));
        }
        StringBuilder sb = new StringBuilder();
        sb.append("SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM ").append(TABLE);
        sb.append(" WHERE TS_HASH IN (");
        boolean first = true;
        for (long h : hashes) {
            if (!first) sb.append(",");
            sb.append(h);
            first = false;
        }
        sb.append(") ORDER BY TS_CD, DATE_VALUE DESC");
        return applyLimit(sb.toString());
    }

    static String generateMultiTickerDateRangeQuery(Random rng) {
        int numTickers = 8 + rng.nextInt(Math.min(5, TS_HASH_POOL.length - 8 + 1));
        Set<Long> hashes = new HashSet<>();
        while (hashes.size() < numTickers) {
            hashes.add(pickTicker(rng));
        }
        int startYear = 2020 + rng.nextInt(4);
        int startMonth = 1 + rng.nextInt(12);
        String startDate = String.format("%d-%02d-01", startYear, startMonth);
        int rangeMonths = 6 + rng.nextInt(24);
        int endYear = startYear + (startMonth + rangeMonths - 1) / 12;
        int endMonth = (startMonth + rangeMonths - 1) % 12 + 1;
        String endDate = String.format("%d-%02d-28", endYear, endMonth);

        StringBuilder sb = new StringBuilder();
        sb.append("SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM ").append(TABLE);
        sb.append(" WHERE TS_HASH IN (");
        boolean first = true;
        for (long h : hashes) {
            if (!first) sb.append(",");
            sb.append(h);
            first = false;
        }
        sb.append(") AND DATE_VALUE BETWEEN '").append(startDate).append("' AND '").append(endDate).append("'");
        sb.append(" ORDER BY TS_CD, DATE_VALUE DESC");
        return applyLimit(sb.toString());
    }

    static boolean isInteractiveTable() {
        return TABLE.toUpperCase().contains("_IT");
    }

    static String applyLimit(String query) {
        if (RESULT_LIMIT > 0) {
            return query + " LIMIT " + RESULT_LIMIT;
        }
        return query;
    }

    static String generateSingleTickerDateRangeQuery(Random rng) {
        long hash = pickTicker(rng);
        int startYear = 2020 + rng.nextInt(4);
        int startMonth = 1 + rng.nextInt(12);
        String startDate = String.format("%d-%02d-01", startYear, startMonth);
        int rangeMonths = 6 + rng.nextInt(24);
        int endYear = startYear + (startMonth + rangeMonths - 1) / 12;
        int endMonth = (startMonth + rangeMonths - 1) % 12 + 1;
        String endDate = String.format("%d-%02d-28", endYear, endMonth);
        return applyLimit("SELECT TS_HASH, TS_CD, DATE_VALUE, DATA_VALUE, DT_LST_UPD FROM " + TABLE +
               " WHERE DATA_VALUE IS NOT NULL AND TS_HASH = " + hash +
               " AND DATE_VALUE BETWEEN '" + startDate + "' AND '" + endDate + "'" +
               " QUALIFY ROW_NUMBER() OVER(PARTITION BY TS_CD, DATE_VALUE ORDER BY DT_LST_UPD DESC) = 1" +
               " ORDER BY 2, 3");
    }

    static String generateSingleTickerQuery(Random rng) {
        long hash = pickTicker(rng);
        if (isInteractiveTable()) {
            return applyLimit("SELECT TS_HASH, TS_CD, DATE_VALUE, DATA_VALUE FROM " + TABLE +
                   " WHERE TS_HASH = " + hash +
                   " ORDER BY DATE_VALUE DESC");
        }
        return applyLimit("SELECT TS_HASH, TS_CD, DATE_VALUE, DATA_VALUE, DT_LST_UPD FROM " + TABLE +
               " WHERE DATA_VALUE IS NOT NULL AND TS_HASH = " + hash +
               " QUALIFY ROW_NUMBER() OVER(PARTITION BY TS_CD, DATE_VALUE ORDER BY DT_LST_UPD DESC) = 1" +
               " ORDER BY 2, 3");
    }

    static void runLoadTest() throws Exception {
        String testStartTs = Instant.now().atZone(ZoneOffset.UTC).format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        long startTime = System.currentTimeMillis();

        ExecutorService executor = Executors.newFixedThreadPool(NUM_CONNECTIONS);
        List<Future<WorkerResult>> futures = new ArrayList<>();
        AtomicInteger activeConnections = new AtomicInteger(0);
        List<long[]> connTimeline = Collections.synchronizedList(new ArrayList<>());

        int rampUp = Math.min(RAMP_UP_SECONDS, DURATION_SECONDS / 2);
        long delayPerConn = NUM_CONNECTIONS > 1 ? (rampUp * 1000L) / NUM_CONNECTIONS : 0;

        for (int i = 0; i < NUM_CONNECTIONS; i++) {
            if (i > 0 && delayPerConn > 0) {
                Thread.sleep(delayPerConn);
            }
            long remaining = DURATION_SECONDS * 1000L - (System.currentTimeMillis() - startTime);
            if (remaining <= 0) break;
            final long dur = remaining;
            futures.add(executor.submit(() -> workerThread(dur, activeConnections, connTimeline)));
        }

        List<WorkerResult> results = new ArrayList<>();
        for (Future<WorkerResult> f : futures) {
            results.add(f.get());
        }
        executor.shutdown();

        long elapsed = System.currentTimeMillis() - startTime;
        String testEndTs = Instant.now().atZone(ZoneOffset.UTC).format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));

        List<Double> allLatencies = new ArrayList<>();
        int totalErrors = 0;
        List<Integer> allRowCounts = new ArrayList<>();
        List<Integer> allChunkCounts = new ArrayList<>();
        Set<Long> allTickers = new HashSet<>();
        List<String> errorMessages = new ArrayList<>();

        for (WorkerResult r : results) {
            allLatencies.addAll(r.latencies);
            allRowCounts.addAll(r.rowCounts);
            allChunkCounts.addAll(r.chunkCounts);
            totalErrors += r.errors;
            allTickers.addAll(r.tickersUsed);
            errorMessages.addAll(r.errorMessages);
        }

        double avgRows = allRowCounts.isEmpty() ? 0 : allRowCounts.stream().mapToInt(Integer::intValue).average().orElse(0);
        int maxRows = allRowCounts.isEmpty() ? 0 : allRowCounts.stream().mapToInt(Integer::intValue).max().orElse(0);

        int chunks1 = 0, chunks2 = 0, chunks3plus = 0;
        for (int c : allChunkCounts) {
            if (c <= 1) chunks1++;
            else if (c == 2) chunks2++;
            else chunks3plus++;
        }

        // Output JSON
        StringBuilder json = new StringBuilder();
        json.append("{");
        json.append("\"query_count\":").append(allLatencies.size()).append(",");
        json.append("\"errors\":").append(totalErrors).append(",");
        json.append("\"elapsed_total\":").append(elapsed / 1000.0).append(",");
        json.append("\"num_connections\":").append(NUM_CONNECTIONS).append(",");
        json.append("\"unique_tickers\":").append(allTickers.size()).append(",");
        json.append("\"avg_rows_per_query\":").append(String.format("%.1f", avgRows)).append(",");
        json.append("\"max_rows_per_query\":").append(maxRows).append(",");
        json.append("\"chunks_1\":").append(chunks1).append(",");
        json.append("\"chunks_2\":").append(chunks2).append(",");
        json.append("\"chunks_3plus\":").append(chunks3plus).append(",");
        json.append("\"test_start_ts\":\"").append(testStartTs).append("\",");
        json.append("\"test_end_ts\":\"").append(testEndTs).append("\",");
        json.append("\"latencies\":[");
        for (int i = 0; i < allLatencies.size(); i++) {
            if (i > 0) json.append(",");
            json.append(String.format("%.4f", allLatencies.get(i)));
        }
        json.append("],");
        json.append("\"conn_timeline\":[");
        for (int i = 0; i < connTimeline.size(); i++) {
            if (i > 0) json.append(",");
            long[] entry = connTimeline.get(i);
            json.append("[").append((entry[0] - startTime) / 1000.0).append(",").append(entry[1]).append("]");
        }
        json.append("],");
        json.append("\"error_messages\":[");
        for (int i = 0; i < Math.min(errorMessages.size(), 10); i++) {
            if (i > 0) json.append(",");
            json.append("\"").append(errorMessages.get(i).replace("\"", "\\\"").replace("\n", " ")).append("\"");
        }
        json.append("],");
        json.append("\"session_v1_query_api\":\"").append(SESSION_V1_QUERY_API).append("\",");
        json.append("\"session_prefetch_threads\":\"").append(SESSION_PREFETCH_THREADS).append("\"");
        json.append("}");

        System.out.println(json.toString());
    }

    static WorkerResult workerThread(long durationMs, AtomicInteger activeConnections, List<long[]> connTimeline) {
        if ("async".equals(EXEC_MODE)) {
            return workerThreadAsync(durationMs, activeConnections, connTimeline);
        }
        return workerThreadSync(durationMs, activeConnections, connTimeline);
    }

    static WorkerResult workerThreadSync(long durationMs, AtomicInteger activeConnections, List<long[]> connTimeline) {
        WorkerResult result = new WorkerResult();
        Random rng = new Random();

        try {
            Connection conn = getConnection();
            Statement stmt = conn.createStatement();
            stmt.execute("USE WAREHOUSE " + WAREHOUSE);
            stmt.execute("ALTER SESSION SET USE_CACHED_RESULT = TRUE");


            int active = activeConnections.incrementAndGet();
            connTimeline.add(new long[]{System.currentTimeMillis(), active});

            long start = System.currentTimeMillis();

            while ((System.currentTimeMillis() - start) < durationMs) {
                ResultSet rs = null;
                try {
                    long t0 = System.nanoTime();

                    String query;
                    if ("tscd_single".equals(QUERY_MIX)) {
                        query = generateTsCdSingleQuery(rng);
                    } else if ("tscd_date".equals(QUERY_MIX)) {
                        query = generateTsCdDateRangeQuery(rng);
                    } else if ("tscd_multi".equals(QUERY_MIX)) {
                        query = generateTsCdMultiQuery(rng);
                    } else if ("tscd_mixed".equals(QUERY_MIX)) {
                        double r = rng.nextDouble();
                        if (r < 0.5) query = generateTsCdSingleQuery(rng);
                        else if (r < 0.8) query = generateTsCdDateRangeQuery(rng);
                        else query = generateTsCdMultiQuery(rng);
                    } else if ("multi".equals(QUERY_MIX)) {
                        query = generateMultiTickerQuery(rng);
                    } else if ("single".equals(QUERY_MIX)) {
                        query = generateSingleTickerQuery(rng);
                    } else if ("multi_date".equals(QUERY_MIX)) {
                        query = generateMultiTickerDateRangeQuery(rng);
                    } else if ("single_date_mix".equals(QUERY_MIX)) {
                        query = rng.nextDouble() < 0.8 ? generateSingleTickerQuery(rng) : generateSingleTickerDateRangeQuery(rng);
                    } else if ("single_date_50".equals(QUERY_MIX)) {
                        query = rng.nextDouble() < 0.5 ? generateSingleTickerQuery(rng) : generateSingleTickerDateRangeQuery(rng);
                    } else if ("single_date_100".equals(QUERY_MIX)) {
                        query = generateSingleTickerDateRangeQuery(rng);
                    } else if ("mixed".equals(QUERY_MIX)) {
                        query = rng.nextDouble() < 0.6 ? generateMultiTickerQuery(rng) : generateSingleTickerQuery(rng);
                    } else {
                        double r = rng.nextDouble();
                        if (r < 0.4) query = generateMultiTickerQuery(rng);
                        else if (r < 0.7) query = generateMultiTickerDateRangeQuery(rng);
                        else query = generateSingleTickerQuery(rng);
                    }
                    rs = stmt.executeQuery(query);

                    int rowCount = 0;
                    while (rs.next()) {
                        rowCount++;
                    }
                    int chunkCount = 1;
                    try {
                        java.lang.reflect.Method m = rs.getClass().getMethod("getFirstChunkRowCount");
                        int firstChunkRows = ((Number) m.invoke(rs)).intValue();
                        if (firstChunkRows > 0 && rowCount > firstChunkRows) {
                            chunkCount = 2;
                            int remaining = rowCount - firstChunkRows;
                            int chunkSize = firstChunkRows;
                            if (chunkSize > 0) {
                                chunkCount = 1 + (int) Math.ceil((double) remaining / chunkSize);
                            }
                        }
                    } catch (Exception ignored) {
                        try {
                            java.lang.reflect.Field f = rs.getClass().getDeclaredField("chunkCount");
                            f.setAccessible(true);
                            chunkCount = f.getInt(rs);
                        } catch (Exception ignored2) {
                            try {
                                java.lang.reflect.Field f = rs.getClass().getDeclaredField("totalChunkCount");
                                f.setAccessible(true);
                                chunkCount = f.getInt(rs);
                            } catch (Exception ignored3) {}
                        }
                    }
                    rs.close();
                    double latency = (System.nanoTime() - t0) / 1_000_000_000.0;
                    result.latencies.add(latency);
                    result.rowCounts.add(rowCount);
                    result.chunkCounts.add(chunkCount);
                } catch (Exception e) {
                    result.errors++;
                    if (result.errorMessages.size() < 3) {
                        result.errorMessages.add(e.getMessage() != null ? e.getMessage().substring(0, Math.min(200, e.getMessage().length())) : "unknown");
                    }
                }
            }

            active = activeConnections.decrementAndGet();
            connTimeline.add(new long[]{System.currentTimeMillis(), active});

            stmt.close();
            conn.close();
        } catch (Exception e) {
            result.errors++;
            if (result.errorMessages.size() < 3) {
                result.errorMessages.add("conn: " + (e.getMessage() != null ? e.getMessage().substring(0, Math.min(200, e.getMessage().length())) : "unknown"));
            }
        }

        return result;
    }

    static WorkerResult workerThreadAsync(long durationMs, AtomicInteger activeConnections, List<long[]> connTimeline) {
        WorkerResult result = new WorkerResult();
        Random rng = new Random();
        int maxInFlight = 8;

        try {
            Connection conn = getConnection();
            Statement stmt = conn.createStatement();
            stmt.execute("USE WAREHOUSE " + WAREHOUSE);
            stmt.execute("ALTER SESSION SET USE_CACHED_RESULT = TRUE");

            net.snowflake.client.api.statement.SnowflakeStatement sfStmt = stmt.unwrap(net.snowflake.client.api.statement.SnowflakeStatement.class);

            int active = activeConnections.incrementAndGet();
            connTimeline.add(new long[]{System.currentTimeMillis(), active});

            long start = System.currentTimeMillis();
            List<long[]> pending = new ArrayList<>(); // [submitTimeNano, 0]
            List<ResultSet> pendingRs = new ArrayList<>();

            while ((System.currentTimeMillis() - start) < durationMs) {
                while (pendingRs.size() < maxInFlight && (System.currentTimeMillis() - start) < durationMs) {
                    String query;
                    if ("multi".equals(QUERY_MIX)) {
                        query = generateMultiTickerQuery(rng);
                    } else if ("single".equals(QUERY_MIX)) {
                        query = generateSingleTickerQuery(rng);
                    } else if ("multi_date".equals(QUERY_MIX)) {
                        query = generateMultiTickerDateRangeQuery(rng);
                    } else if ("single_date_mix".equals(QUERY_MIX)) {
                        query = rng.nextDouble() < 0.8 ? generateSingleTickerQuery(rng) : generateSingleTickerDateRangeQuery(rng);
                    } else if ("single_date_50".equals(QUERY_MIX)) {
                        query = rng.nextDouble() < 0.5 ? generateSingleTickerQuery(rng) : generateSingleTickerDateRangeQuery(rng);
                    } else if ("single_date_100".equals(QUERY_MIX)) {
                        query = generateSingleTickerDateRangeQuery(rng);
                    } else if ("tscd_single".equals(QUERY_MIX)) {
                        query = generateTsCdSingleQuery(rng);
                    } else if ("tscd_date".equals(QUERY_MIX)) {
                        query = generateTsCdDateRangeQuery(rng);
                    } else if ("tscd_multi".equals(QUERY_MIX)) {
                        query = generateTsCdMultiQuery(rng);
                    } else if ("tscd_mixed".equals(QUERY_MIX)) {
                        double r = rng.nextDouble();
                        if (r < 0.5) query = generateTsCdSingleQuery(rng);
                        else if (r < 0.8) query = generateTsCdDateRangeQuery(rng);
                        else query = generateTsCdMultiQuery(rng);
                    } else if ("mixed".equals(QUERY_MIX)) {
                        query = rng.nextDouble() < 0.6 ? generateMultiTickerQuery(rng) : generateSingleTickerQuery(rng);
                    } else {
                        double r = rng.nextDouble();
                        if (r < 0.4) query = generateMultiTickerQuery(rng);
                        else if (r < 0.7) query = generateMultiTickerDateRangeQuery(rng);
                        else query = generateSingleTickerQuery(rng);
                    }
                    try {
                        long t0 = System.nanoTime();
                        ResultSet rs = sfStmt.executeAsyncQuery(query);
                        pending.add(new long[]{t0});
                        pendingRs.add(rs);
                    } catch (Exception e) {
                        result.errors++;
                        if (result.errorMessages.size() < 3) {
                            result.errorMessages.add("submit: " + (e.getMessage() != null ? e.getMessage().substring(0, Math.min(200, e.getMessage().length())) : "unknown"));
                        }
                    }
                }

                List<Integer> completed = new ArrayList<>();
                for (int i = 0; i < pendingRs.size(); i++) {
                    try {
                        ResultSet rs = pendingRs.get(i);
                        net.snowflake.client.api.resultset.SnowflakeAsyncResultSet sfRs = rs.unwrap(net.snowflake.client.api.resultset.SnowflakeAsyncResultSet.class);
                        if (sfRs.getStatus().isStillRunning()) {
                            continue;
                        }
                        while (rs.next()) {}
                        rs.close();
                        double latency = (System.nanoTime() - pending.get(i)[0]) / 1_000_000_000.0;
                        result.latencies.add(latency);
                        completed.add(i);
                    } catch (Exception e) {
                        result.errors++;
                        if (result.errorMessages.size() < 3) {
                            result.errorMessages.add("poll: " + (e.getMessage() != null ? e.getMessage().substring(0, Math.min(200, e.getMessage().length())) : "unknown"));
                        }
                        completed.add(i);
                    }
                }
                for (int i = completed.size() - 1; i >= 0; i--) {
                    int idx = completed.get(i);
                    pending.remove(idx);
                    pendingRs.remove(idx);
                }
                if (completed.isEmpty()) {
                    Thread.sleep(5);
                }
            }

            for (int i = 0; i < pendingRs.size(); i++) {
                try {
                    ResultSet rs = pendingRs.get(i);
                    net.snowflake.client.api.resultset.SnowflakeAsyncResultSet sfRs = rs.unwrap(net.snowflake.client.api.resultset.SnowflakeAsyncResultSet.class);
                    while (sfRs.getStatus().isStillRunning()) {
                        Thread.sleep(10);
                    }
                    while (rs.next()) {}
                    rs.close();
                    double latency = (System.nanoTime() - pending.get(i)[0]) / 1_000_000_000.0;
                    result.latencies.add(latency);
                } catch (Exception e) {
                    result.errors++;
                }
            }

            active = activeConnections.decrementAndGet();
            connTimeline.add(new long[]{System.currentTimeMillis(), active});

            stmt.close();
            conn.close();
        } catch (Exception e) {
            result.errors++;
            if (result.errorMessages.size() < 3) {
                result.errorMessages.add("conn: " + (e.getMessage() != null ? e.getMessage().substring(0, Math.min(200, e.getMessage().length())) : "unknown"));
            }
        }

        return result;
    }

    static String getArg(String[] args, String name, String defaultVal) {
        for (int i = 0; i < args.length - 1; i++) {
            if (args[i].equals(name)) return args[i + 1];
        }
        return defaultVal;
    }

    static class WorkerResult {
        List<Double> latencies = new ArrayList<>();
        List<Integer> rowCounts = new ArrayList<>();
        List<Integer> chunkCounts = new ArrayList<>();
        int errors = 0;
        Set<Long> tickersUsed = new HashSet<>();
        List<String> errorMessages = new ArrayList<>();
    }
}

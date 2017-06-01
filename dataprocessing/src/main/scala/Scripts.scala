import org.apache.spark.{SparkConf, SparkContext}
import com.datastax.spark.connector._
import com.datastax.spark.connector.rdd.CassandraTableScanRDD
import java.util.{Calendar, Date}
import org.apache.commons.lang.time.DateUtils //Loads implicit functions

object Scripts extends App {

	val keyspaceName = "data"

	val conf: SparkConf = new SparkConf(true)
			.set("spark.cassandra.connection.host", "127.0.0.1:9042")
			.set("spark.cassandra.auth.username", "cassandra")
			.set("spark.cassandra.auth.password", "cassandra")

	val sc = new SparkContext("spark://192.168.123.10:7077", "test", conf)

	/**
	  * Compute the delta for from to to, exclusive to.
	  *
	  * @param from The timestamp for the beginning
	  * @param to   The timestamp for the end
	  */
	def computeDelta(from: Long, to: Long): Unit = {
		val events: CassandraTableScanRDD[CassandraRow] = sc.cassandraTable(keyspaceName, "events")
		val rows = events.where("timestamp >= ? AND timestamp <= ?", from, to)

		events.map(_.getInt("parking")).foreach { parking =>
			val toSave = from.to(to, 3600)
					.map(computeDelta(_, parking, rows))
					.map { case (timestamp, delta) => (parking, timestamp, delta) }
					.toList
			sc.parallelize(toSave).saveToCassandra(keyspaceName, "park_stat_delta", SomeColumns("parking", "timestamp", "delta"))
		}
	}

	/**
	  * Compute de delta from a given hour and parking.
	  * The delta is computed as the number of input minus the output.
	  *
	  * @param h       The hour
	  * @param parking The parking
	  * @param rows    The rows
	  * @return
	  */
	def computeDelta(h: Long, parking: Int, rows: CassandraTableScanRDD[CassandraRow]): (Long, Long) = {
		val rowsToCompute = rows.where("timestamp >= ? AND timestamp < ? && parking = ?", h, h + 3600, parking)
		val in = rowsToCompute.where("type = ?", "IN").count()
		val out = rowsToCompute.where("type = ?", "OUT").count()
		h -> (in - out)
	}

	/**
	  * Returns the floored hour from a timestamp :
	  *
	  * For example, if you had the datetime of 28 Mar 2002
	  * 13:45:01.231, it would return 28 Mar 2002 13:00:00.000.
	  *
	  * @param timestamp The timestamp to floor
	  * @return The floored timestamp
	  */
	def floor(timestamp: Long): Long = {
		DateUtils.truncate(new Date(timestamp), Calendar.HOUR).getTime
	}

}

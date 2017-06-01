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

	def table(name: String): CassandraTableScanRDD[CassandraRow] = sc.cassandraTable(keyspaceName, name)

	/**
	  * Compute the delta for from to to, exclusive to.
	  *
	  * @param from The timestamp for the beginning
	  * @param to   The timestamp for the end
	  */
	def computeDelta(from: Long, to: Long, step: Long = 3600): Unit = {
		case class ParkStatDelta(parking: Int, timestamp: Long, delta: Int)
		val events = table("events")
		val rows = events.where("timestamp >= ? AND timestamp <= ?", from, to)

		events.map(_.getInt("parking")).foreach(parking => {
			val toSave = from.to(to, step)
					.map(computeDelta(_, parking, rows))
					.map { case (timestamp, delta) => ParkStatDelta(parking, timestamp, delta.toInt) }
					.toList
			sc.parallelize(toSave).saveToCassandra(keyspaceName, "park_stat_delta", SomeColumns("parking", "timestamp", "delta"))
		})
	}

	/**
	  * Resolve the delta for the given hour.
	  *
	  * @param hour the hour
	  */
	def resolveDelta(hour: Long): Unit = {
		case class ParkStat(parking: Int, timestamp: Long, count: Int)
		val statDeltas = table("park_stat_delta").where("timestamp >= ? AND timestamp <= ?", hour - 3600, hour)
		val stats = table("park_stat")

		statDeltas.map(_.getInt("parking")).foreach(parking => {
			val before = stats.where("timestamp = ? AND parking = ?", hour - 3600, parking).first.getInt("count")
			val current = before + statDeltas.where("parking = ?", parking).first.getInt("delta")
			sc.parallelize(List(ParkStat(parking, hour, current)))
					.saveToCassandra(keyspaceName, "park_stat", SomeColumns("parking", "timestamp", "count"))
		})
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

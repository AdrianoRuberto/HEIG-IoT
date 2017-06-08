import org.apache.spark.{SparkConf, SparkContext}
import com.datastax.spark.connector._
import com.datastax.spark.connector.rdd.CassandraTableScanRDD
import com.typesafe.config.ConfigFactory
import java.util.{Calendar, Date}
import org.apache.commons.lang.time.DateUtils //Loads implicit functions

object Scripts extends App {

	val cassandraConf = ConfigFactory.load("application.conf")

	val keyspaceName = cassandraConf.getString("spark.cassandra.keyspace_name")

	val conf: SparkConf = new SparkConf(true)
			.set("spark.cassandra.connection.host", cassandraConf.getString("spark.cassandra.host"))
			.set("spark.cassandra.auth.username", cassandraConf.getString("spark.cassandra.username"))
			.set("spark.cassandra.auth.password", cassandraConf.getString("spark.cassandra.password"))

	// implicit val sc = new SparkContext("spark://" + cassandraConf.getString("spark.context.host"),
	// 	cassandraConf.getString("spark.context.appName"), conf)

	implicit val sc = new SparkContext(conf)

	def table(name: String): CassandraTableScanRDD[CassandraRow] = sc.cassandraTable(keyspaceName, name)

	case class ParkStat(parking: Int, timestamp: Long, count: Int)
	case class ParkStatDelta(parking: Int, timestamp: Long, delta: Int)

	/**
	  * Compute the delta for from to to, exclusive to.
	  *
	  * @param from The timestamp for the beginning
	  * @param to   The timestamp for the end
	  */
	def computeDelta(from: Long, to: Long, step: Long = 3600): Unit = {
		val events = table("events")
		val rows = events.where("timestamp >= ? AND timestamp <= ?", from, to)

		events.map(_.getInt("parking")).foreach(parking => {
			val toSave = from.to(to, step)
					.map(hour => hour -> computeDelta(hour, hour + step, parking, rows))
					.map { case (timestamp, delta) => ParkStatDelta(parking, timestamp, delta.toInt) }
					.toList
			sc.parallelize(toSave).saveToCassandra(keyspaceName, "park_stat_delta", SomeColumns("parking", "timestamp", "delta"))
		})
	}

	/**
	  * Compute de delta from given timestamps and parking until the next step.
	  * The delta is computed as the number of input minus the output.
	  *
	  * @param from    The timestamp for the beginning
	  * @param to      The timestamp for the end
	  * @param parking The parking
	  * @param rows    The rows
	  * @return
	  */
	def computeDelta(from: Long, to: Long, parking: Int, rows: CassandraTableScanRDD[CassandraRow]): Int = {
		val rowsToCompute = rows.where("timestamp >= ? AND timestamp < ? && parking = ?", from, to, parking)
		val in = rowsToCompute.where("type = ?", "IN").count()
		val out = rowsToCompute.where("type = ?", "OUT").count()
		(in - out).toInt
	}

	/**
	  * Resolve the delta for the given hour.
	  *
	  * @param hour the hour
	  */
	def resolveDelta(hour: Long): Unit = {
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

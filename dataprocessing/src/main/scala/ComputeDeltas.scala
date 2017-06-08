import com.datastax.spark.connector._
import com.typesafe.config.ConfigFactory
import org.apache.spark.{SparkConf, SparkContext}

/**
  * @author ldavid
  * @created 6/8/17
  */
object ComputeDeltas {
  case class ParkStatDelta(parking: Int, timestamp: Long, delta: Int)

  def main(args: Array[String]): Unit = {

    val parking = args(0).toInt

    val cassandraConf = ConfigFactory.load()
    implicit val keyspaceName = cassandraConf.getString("cassandra.keyspace_name")
    val conf: SparkConf = new SparkConf(true)
      .setAppName("ComputeDeltas")
      .set("spark.cassandra.connection.host", cassandraConf.getString("cassandra.host"))

    implicit val sc = new SparkContext(conf)

    val events = table("events").where("""parking = ? and device = 'flir'""", parking)



    val deltas = events
      .map(ComputeDeltas.groupByHour)
      .reduceByKey(_ + _)
      .map({ case (t, d) => ParkStatDelta(parking, t, d) })
      .saveToCassandra(keyspaceName, "park_stat_delta")

    /* deltas.foreach {
      case (p, t, d) => println(s"$p : $t : $d")
    } */

    sc.stop()
  }

  private def groupByHour(row: CassandraRow): (Long, Int) = {
    val timestamp = row.getDateTime("timestamp")
      .withMinuteOfHour(0)
      .withSecondOfMinute(0)
      .withMillisOfSecond(0)
      .toInstant
      .getMillis

    val typ = row.getString("type")

    typ match {
      case "in" => (timestamp, 1)
      case "out" => (timestamp, -1)
    }
  }

  private def table(name: String)(implicit keyspace: String, sc: SparkContext) = sc.cassandraTable(keyspace, name)

}

<?php 

require('dbconn.inc');

$map = array(
  5 => 1,
  /*1 => 4,
  9 => 9,
  18 => 6,
  7 => 6,
  6 => 6,
  11 => 6,
  16 => 6,
  14 => 6,
  17 => 6,
  21 => 6,
  25 => 6*/
);

header("Content-type: text/plain");

foreach($map as $old_cat => $new_cat) {
  $sql = "SELECT id FROM circuits_circuit WHERE category='$old_cat'";

  $res = pg_query($dbconn, $sql);

  while($row = pg_fetch_assoc($res)) {
    echo sprintf("UPDATE circuits_circuit SET category='%d' WHERE id='%d';\n", $new_cat, $row["id"]);
  }
}

?>

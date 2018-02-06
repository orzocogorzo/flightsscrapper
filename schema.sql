CREATE TABLE IF NOT EXISTS flights (
  adshex CHAR(20),
  flight_id CHAR(20),
  lat CHAR(20),
  lng CHAR(20),
  track CHAR(20),
  alt CHAR(20),
  speed CHAR(20),
  squawk CHAR(20),
  radar CHAR(24),
  type CHAR(12),
  registration CHAR(24),
  timestamp CHAR(30),
  s_airport CHAR(5),
  t_airport CHAR(5),
  IATA CHAR(10),
  unknown1 CHAR(10),
  unknown2 CHAR(10),
  OACI CHAR(10),
  unknown3 CHAR(10)
)


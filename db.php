<?php
// Crypto Nexus Ultra - Database Connection
// Intentionally vulnerable to SQL Injection

class VulnerableDB {
    private $connection;
    
    public function __construct() {
        $host = $_ENV['DB_HOST'] ?? 'mysql_internal';
        $user = 'root';
        $pass = $_ENV['DB_ROOT_PASSWORD'] ?? 'RootPassword123!';
        $db   = 'crypto_nexus';
        
        // ¡VULNERABLE! Sin preparación de statements
        $this->connection = new mysqli($host, $user, $pass, $db);
        
        if($this->connection->connect_error) {
            die("Connection failed: " . $this->connection->connect_error);
        }
        
        // Configuración insegura
        $this->connection->query("SET NAMES 'utf8'");
        $this->connection->query("SET sql_mode = ''"); // ¡Deshabilita protecciones!
    }
    
    // Método extremadamente vulnerable
    public function rawQuery($sql) {
        // ¡EJECUCIÓN DIRECTA SIN SANITIZACIÓN!
        $result = $this->connection->query($sql);
        
        if(!$result) {
            // ¡Devuelve errores detallados (SQL Error-based Injection)!
            return [
                'error' => true,
                'message' => $this->connection->error,
                'sql' => $sql
            ];
        }
        
        return $result;
    }
    
    // SELECT vulnerable
    public function select($table, $where = '1=1', $columns = '*') {
        $sql = "SELECT $columns FROM $table WHERE $where";
        return $this->rawQuery($sql);
    }
    
    // INSERT vulnerable
    public function insert($table, $data) {
        $columns = implode(', ', array_keys($data));
        $values = "'" . implode("', '", array_values($data)) . "'";
        $sql = "INSERT INTO $table ($columns) VALUES ($values)";
        return $this->rawQuery($sql);
    }
    
    // UPDATE vulnerable
    public function update($table, $data, $where) {
        $set = [];
        foreach($data as $key => $value) {
            $set[] = "$key = '$value'";
        }
        $setClause = implode(', ', $set);
        $sql = "UPDATE $table SET $setClause WHERE $where";
        return $this->rawQuery($sql);
    }
    
    // DELETE vulnerable
    public function delete($table, $where) {
        $sql = "DELETE FROM $table WHERE $where";
        return $this->rawQuery($sql);
    }
    
    // UNION-based injection helper
    public function unionInjection($query) {
        // Construye query para UNION-based injection
        $sql = "(SELECT NULL, NULL, NULL) UNION ALL $query";
        return $this->rawQuery($sql);
    }
    
    // Time-based blind SQLi
    public function timeBasedQuery($condition) {
        $sql = "SELECT IF($condition, SLEEP(5), 0)";
        return $this->rawQuery($sql);
    }
    
    // File read vulnerability
    public function readFile($path) {
        $sql = "SELECT LOAD_FILE('$path') as content";
        $result = $this->rawQuery($sql);
        if($result && $row = $result->fetch_assoc()) {
            return $row['content'];
        }
        return null;
    }
    
    // File write vulnerability (RCE potential!)
    public function writeFile($path, $content) {
        $content = $this->connection->real_escape_string($content);
        $sql = "SELECT '$content' INTO OUTFILE '$path'";
        return $this->rawQuery($sql);
    }
    
    // Execute system commands through MySQL (RCE)
    public function executeCommand($cmd) {
        $sql = "SELECT sys_exec('$cmd')";
        return $this->rawQuery($sql);
    }
    
    // Get database credentials (for escalation)
    public function getCredentials() {
        $sql = "SELECT User, Password FROM mysql.user WHERE User = 'root'";
        return $this->rawQuery($sql);
    }
    
    public function __destruct() {
        if($this->connection) {
            $this->connection->close();
        }
    }
}

// Instancia global vulnerable
$db = new VulnerableDB();

// Función helper para inyecciones
function getUserByID($id) {
    global $db;
    // ¡VULNERABLE! Concatenación directa
    $result = $db->rawQuery("SELECT * FROM users WHERE id = $id");
    return $result->fetch_assoc();
}

function searchUsers($search) {
    global $db;
    // ¡VULNERABLE LIKE injection!
    $result = $db->rawQuery("SELECT * FROM users WHERE username LIKE '%$search%' OR email LIKE '%$search%'");
    return $result;
}

// Authentication vulnerable function
function authenticate($username, $password) {
    global $db;
    
    // ¡VULNERABLE! Password en texto plano comparado en SQL
    $sql = "SELECT * FROM users WHERE username = '$username' AND password_hash = MD5('$password')";
    $result = $db->rawQuery($sql);
    
    if($result && $result->num_rows > 0) {
        return $result->fetch_assoc();
    }
    
    return false;
}

// Ejemplo de endpoint vulnerable
if(isset($_GET['test_injection'])) {
    $id = $_GET['id'];
    $user = getUserByID($id);
    echo json_encode($user);
    exit;
}

// Debug endpoint para mostrar queries
if(isset($_GET['debug'])) {
    echo "<pre>";
    echo "DB Connection: Active\n";
    echo "Vulnerabilities enabled:\n";
    echo "  - SQL Injection (Union, Error, Time-based)\n";
    echo "  - File Read/Write via SQL\n";
    echo "  - Command Execution via sys_exec\n";
    echo "  - Credential Exposure\n";
    echo "\nTest queries:\n";
    echo "  ?id=1 UNION SELECT 1,2,3,version(),5,6,7,8,9,10\n";
    echo "  ?id=1 AND SLEEP(5)--\n";
    echo "  ?id=1 AND ExtractValue(1,CONCAT(0x7e,(SELECT @@version),0x7e))\n";
    echo "</pre>";
    exit;
}
?>

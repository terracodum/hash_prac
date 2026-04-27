using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("=== Iris Classifier (C# → Python) ===");
        Console.WriteLine("Введите 4 признака через пробел:");
        Console.WriteLine("  sepal_length  sepal_width  petal_length  petal_width");
        Console.WriteLine("Пример: 5.1 3.5 1.4 0.2  (setosa)");
        Console.Write("> ");

        string? line = Console.ReadLine();
        if (string.IsNullOrWhiteSpace(line))
        {
            Console.WriteLine("Нет ввода.");
            return;
        }

        string[] parts = line.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length != 4)
        {
            Console.WriteLine($"Ошибка: нужно 4 числа, получено {parts.Length}.");
            return;
        }

        double[] features = new double[4];
        for (int i = 0; i < 4; i++)
        {
            if (!double.TryParse(parts[i],
                System.Globalization.NumberStyles.Float,
                System.Globalization.CultureInfo.InvariantCulture,
                out features[i]))
            {
                Console.WriteLine($"Ошибка: '{parts[i]}' не является числом.");
                return;
            }
        }

        // Формируем JSON-аргумент
        string jsonPayload = JsonSerializer.Serialize(new { features });

        // Ищем predict.py относительно этого файла
        string scriptPath = Path.Combine(
            AppContext.BaseDirectory, "..", "..", "..", "..",
            "ml_pipeline", "predict.py");
        scriptPath = Path.GetFullPath(scriptPath);

        if (!File.Exists(scriptPath))
        {
            Console.WriteLine($"Ошибка: скрипт не найден: {scriptPath}");
            return;
        }

        var psi = new ProcessStartInfo
        {
            FileName               = "py",
            Arguments              = $"-3.12 \"{scriptPath}\" \"{jsonPayload.Replace("\"", "\\\"")}\"",
            RedirectStandardOutput = true,
            RedirectStandardError  = true,
            UseShellExecute        = false,
            StandardOutputEncoding = System.Text.Encoding.UTF8,
        };

        try
        {
            using var proc = Process.Start(psi)!;
            string stdout = proc.StandardOutput.ReadToEnd();
            string stderr = proc.StandardError.ReadToEnd();
            proc.WaitForExit();

            if (proc.ExitCode != 0 || string.IsNullOrWhiteSpace(stdout))
            {
                Console.WriteLine($"Python завершился с кодом {proc.ExitCode}");
                if (!string.IsNullOrWhiteSpace(stderr))
                    Console.WriteLine($"stderr: {stderr}");
                return;
            }

            // Красивый вывод результата
            using var doc = JsonDocument.Parse(stdout);
            var root = doc.RootElement;

            if (root.TryGetProperty("error", out var err))
            {
                Console.WriteLine($"Ошибка из Python: {err}");
                return;
            }

            Console.WriteLine($"\nПредсказание: {root.GetProperty("class").GetString()} " +
                              $"(класс {root.GetProperty("prediction").GetInt32()})");

            Console.WriteLine("Вероятности:");
            foreach (var p in root.GetProperty("probabilities").EnumerateObject())
                Console.WriteLine($"  {p.Name,-15} {p.Value.GetDouble():P1}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Ошибка запуска Python: {ex.Message}");
        }
    }
}

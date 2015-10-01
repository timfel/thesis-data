module Benchmark
  module IPS
    class Job
      class StdoutReport
        def start_warming
          $stdout.puts "Calculating -------------------------------------"
        end

        def warming(label, _warmup)
          $stdout.print rjust(label)
        end

        def warmup_stats(_warmup_time_us, timing)
          case format
          when :human
            $stdout.printf "%s i/100ms\n", Helpers.scale(timing)
          else
            $stdout.printf "%10d i/100ms\n", timing
          end
        end

        alias_method :running, :warming
        alias_method :start_running, :start_warming

        def add_report(item, caller)
          $stdout.puts " #{item.body}"
        end

        private

        # @return [Symbol] format used for benchmarking
        def format
          Benchmark::IPS.options[:format]
        end

        # Add padding to label's right if label's length < 20,
        # Otherwise add a new line and 20 whitespaces.
        # @return [String] Right justified label.
        def rjust(label)
          label = label.to_s
          if label.size > 20
            "#{label}\n#{' ' * 20}"
          else
            label.rjust(20)
          end
        end
      end
    end
  end
end

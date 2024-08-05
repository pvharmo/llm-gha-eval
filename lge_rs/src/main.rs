use clap::Parser;
use dotenv::dotenv;

pub mod assistant;
pub mod evaluation;
pub mod inference;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    #[arg(short, long)]
    inference: bool,

    #[arg(short, long)]
    run_id: Option<u64>,
}

fn main() {
    // rayon::ThreadPoolBuilder::new().num_threads(4).build_global().unwrap();
    dotenv().ok();

    if Args::parse().inference {
        println!("Running inference");
        inference::run();
    } else if !Args::parse().run_id.is_none() {
        evaluation::run(Args::parse().run_id.unwrap());
    } else {
        println!("invalid arguments")
    }
}

from {{cookiecutter.project_slug}}.analyze import analyze
from {{cookiecutter.project_slug}}.cli import arguments, pretty_string_from_dict
from {{cookiecutter.project_slug}}.fileio import read_data, save_figures, save_report, process_existing_file_name, process_directory_name
from {{cookiecutter.project_slug}}.plot import plot, show


def main():
    # Arguments and input
    args = arguments()
    input_data_file = process_existing_file_name(args.data_file)

    # DO STUFF HERE
    data = read_data(input_data_file)
    processed, report = analyze(data)
    print(pretty_string_from_dict(report))
    figs = plot(processed)

    # Output
    if args.final:
        output_dir = process_directory_name(args.output_dir, default="results")
        prefix = args.name
        save_figures(figs, path=output_dir, prefix=prefix)
        save_report(report, path=output_dir, prefix=prefix)
        print("Figures and report saved in " + str(output_dir))
    else:
        show()


if __name__ == "__main__":
    main()